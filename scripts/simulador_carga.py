import argparse
import csv
import json
import random
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "carga" / "perfiles.json"
EVIDENCE_ROOT = ROOT / "evidencia" / "ejecuciones"


def utc_now():
    return datetime.now(timezone.utc)


def percentile(values, quantile):
    if not values:
        return None
    ordered = sorted(values)
    index = int((len(ordered) - 1) * quantile)
    return round(ordered[index], 3)


def parse_size_mib(value):
    text = value.strip()
    units = {
        "B": 1 / (1024 * 1024),
        "kB": 1000 / (1024 * 1024),
        "KB": 1 / 1024,
        "KiB": 1 / 1024,
        "MB": 1000 * 1000 / (1024 * 1024),
        "MiB": 1,
        "GB": 1000 * 1000 * 1000 / (1024 * 1024),
        "GiB": 1024,
    }
    for unit in sorted(units, key=len, reverse=True):
        if text.endswith(unit):
            number = float(text[: -len(unit)].strip())
            return round(number * units[unit], 3)
    raise ValueError(f"Unidad de memoria no soportada: {value}")


def load_config(path):
    with Path(path).open(encoding="utf-8") as handle:
        config = json.load(handle)
    operations = config["operations"]
    if sum(item["weight"] for item in operations) != 100:
        raise ValueError("Los pesos de operaciones deben sumar 100")
    seeds = [item["seed"] for item in config["profiles"].values()]
    if len(seeds) != len(set(seeds)):
        raise ValueError("Cada perfil debe tener una semilla diferente")
    return config


def git_value(*args):
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def blocking_git_changes(status):
    lines = [line for line in status.splitlines() if line.strip()]
    allowed_prefix = "?? evidencia/ejecuciones/carga-"
    return [line for line in lines if not line.startswith(allowed_prefix)]


def request_once(base_url, operation, timeout, request_id, repetition):
    started = utc_now()
    watch = time.perf_counter()
    status = 0
    error = ""
    try:
        request = Request(
            base_url.rstrip("/") + operation["path"],
            headers={"Accept": "application/json", "User-Agent": "fixture2030-load/1"},
            method="GET",
        )
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            response.read()
    except HTTPError as exc:
        status = exc.code
        error = f"HTTP {exc.code}"
    except (URLError, TimeoutError, OSError) as exc:
        error = f"{type(exc).__name__}: {str(exc)[:160]}"
    latency_ms = (time.perf_counter() - watch) * 1000
    return {
        "requestId": request_id,
        "repetition": repetition,
        "operation": operation["name"],
        "method": "GET",
        "path": operation["path"],
        "status": status,
        "ok": 200 <= status < 300,
        "latencyMs": round(latency_ms, 3),
        "error": error,
        "startedAtUtc": started.isoformat(),
    }


def docker_sample(containers):
    completed = subprocess.run(
        ["docker", "stats", "--no-stream", "--format", "{{json .}}", *containers],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    captured = utc_now().isoformat()
    rows = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        memory_used = item.get("MemUsage", "0B / 0B").split("/")[0].strip()
        rows.append(
            {
                "capturedAtUtc": captured,
                "container": item.get("Name", item.get("Container", "unknown")),
                "cpuPct": float(item.get("CPUPerc", "0").rstrip("%")),
                "memoryMiB": parse_size_mib(memory_used),
                "netIO": item.get("NetIO", ""),
                "blockIO": item.get("BlockIO", ""),
                "pids": item.get("PIDs", ""),
            }
        )
    return rows


class ResourceMonitor:
    def __init__(self, containers, interval):
        self.containers = containers
        self.interval = interval
        self.samples = []
        self.warnings = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=30)

    def _run(self):
        while not self._stop.is_set():
            try:
                self.samples.extend(docker_sample(self.containers))
            except Exception as exc:
                self.warnings.append(f"{type(exc).__name__}: {str(exc)[:200]}")
            self._stop.wait(self.interval)


def summarize_requests(rows, elapsed_seconds):
    latencies = [row["latencyMs"] for row in rows]
    successes = sum(1 for row in rows if row["ok"])
    total = len(rows)
    return {
        "requests": total,
        "successes": successes,
        "errors": total - successes,
        "errorRatePct": round(((total - successes) * 100 / total), 4) if total else 0,
        "p50Ms": percentile(latencies, 0.50),
        "p95Ms": percentile(latencies, 0.95),
        "p99Ms": percentile(latencies, 0.99),
        "maxMs": round(max(latencies), 3) if latencies else None,
        "elapsedSeconds": round(elapsed_seconds, 3),
        "throughputReqS": round(total / elapsed_seconds, 3) if elapsed_seconds else 0,
    }


def summarize_operations(rows, elapsed_seconds):
    result = {}
    for name in sorted({row["operation"] for row in rows}):
        selected = [row for row in rows if row["operation"] == name]
        result[name] = summarize_requests(selected, elapsed_seconds)
    return result


def summarize_resources(samples):
    result = {}
    for container in sorted({row["container"] for row in samples}):
        selected = [row for row in samples if row["container"] == container]
        cpu = [row["cpuPct"] for row in selected]
        memory = [row["memoryMiB"] for row in selected]
        result[container] = {
            "samples": len(selected),
            "cpuAvgPct": round(sum(cpu) / len(cpu), 3),
            "cpuMaxPct": round(max(cpu), 3),
            "memoryAvgMiB": round(sum(memory) / len(memory), 3),
            "memoryMaxMiB": round(max(memory), 3),
        }
    return result


def evaluate_slo(summary, slo):
    if slo is None:
        return {
            "evaluated": False,
            "passed": None,
            "reason": "El perfil de estres busca el limite; no usa un SLO de aprobacion.",
        }
    checks = {
        "errorRatePct": summary["errorRatePct"] <= slo["maxErrorRatePct"],
        "p95Ms": summary["p95Ms"] <= slo["maxP95Ms"],
        "p99Ms": summary["p99Ms"] <= slo["maxP99Ms"],
    }
    return {"evaluated": True, "passed": all(checks.values()), "objectives": slo, "checks": checks}


def write_csv(path, rows, fieldnames):
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def warm_up(base_url, operations, timeout):
    failures = []
    for index, operation in enumerate(operations, start=1):
        result = request_once(base_url, operation, timeout, f"warmup-{index}", 0)
        if not result["ok"]:
            failures.append({"operation": operation["name"], "status": result["status"], "error": result["error"]})
    if failures:
        raise RuntimeError(f"El warm-up fallo: {failures}")


def run_repetition(config, profile, profile_name, repetition, base_url):
    seed = profile["seed"] + (repetition - 1) * 100000
    randomizer = random.Random(seed)
    operations = config["operations"]
    names = list(range(len(operations)))
    weights = [item["weight"] for item in operations]
    total = profile["durationSeconds"] * profile["targetRps"]
    schedule = randomizer.choices(names, weights=weights, k=total)
    monitor = ResourceMonitor(config["containers"], config["resourceSampleSeconds"])
    rows = []
    started = time.perf_counter()
    monitor.start()
    try:
        with ThreadPoolExecutor(max_workers=profile["concurrency"]) as executor:
            futures = []
            for index, operation_index in enumerate(schedule):
                due = started + (index / profile["targetRps"])
                remaining = due - time.perf_counter()
                if remaining > 0:
                    time.sleep(remaining)
                futures.append(
                    executor.submit(
                        request_once,
                        base_url,
                        operations[operation_index],
                        config["timeoutSeconds"],
                        f"{profile_name}-{repetition:02d}-{index + 1:06d}",
                        repetition,
                    )
                )
            for future in as_completed(futures):
                rows.append(future.result())
    finally:
        monitor.stop()
    elapsed = time.perf_counter() - started
    rows.sort(key=lambda item: item["requestId"])
    return {
        "repetition": repetition,
        "seed": seed,
        "summary": summarize_requests(rows, elapsed),
        "perOperation": summarize_operations(rows, elapsed),
        "resourceSummary": summarize_resources(monitor.samples),
        "resourceWarnings": monitor.warnings,
    }, rows, monitor.samples


def main():
    parser = argparse.ArgumentParser(description="Simulador reproducible de carga de Fixture2030")
    parser.add_argument("--profile", choices=("humo", "normal", "estres"), required=True)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--base-url")
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    profile = dict(config["profiles"][args.profile])
    if args.repetitions is not None:
        if args.repetitions < 1 or args.repetitions > 10:
            raise ValueError("repetitions debe estar entre 1 y 10")
        profile["repetitions"] = args.repetitions
    base_url = args.base_url or config["baseUrl"]
    status = git_value("status", "--short", "--untracked-files=all")
    blocking_changes = blocking_git_changes(status)
    if blocking_changes and not args.allow_dirty:
        raise RuntimeError(
            "El codigo y la configuracion deben estar versionados antes de medir. "
            f"Cambios bloqueantes: {blocking_changes}"
        )
    commit = git_value("rev-parse", "HEAD")
    branch = git_value("branch", "--show-current")

    warm_up(base_url, config["operations"], config["timeoutSeconds"])
    run_id = utc_now().strftime("%Y%m%dT%H%M%SZ")
    output_dir = EVIDENCE_ROOT / f"carga-{args.profile}-{run_id}"
    output_dir.mkdir(parents=True, exist_ok=False)
    repetitions = []
    all_rows = []
    all_resources = []
    total_elapsed = 0.0

    for repetition in range(1, profile["repetitions"] + 1):
        print(f"{repetition}/{profile['repetitions']} Ejecutando perfil {args.profile}...")
        result, rows, resources = run_repetition(
            config, profile, args.profile, repetition, base_url
        )
        repetitions.append(result)
        all_rows.extend(rows)
        all_resources.extend(resources)
        total_elapsed += result["summary"]["elapsedSeconds"]
        write_csv(
            output_dir / f"solicitudes-rep-{repetition:02d}.csv",
            rows,
            ["requestId", "repetition", "operation", "method", "path", "status", "ok", "latencyMs", "error", "startedAtUtc"],
        )
        write_csv(
            output_dir / f"recursos-rep-{repetition:02d}.csv",
            resources,
            ["capturedAtUtc", "container", "cpuPct", "memoryMiB", "netIO", "blockIO", "pids"],
        )
        if repetition < profile["repetitions"]:
            time.sleep(config["recoverySeconds"])

    overall = summarize_requests(all_rows, total_elapsed)
    result = {
        "scenario": f"carga-{args.profile}",
        "classification": "medido",
        "sourceCommit": commit,
        "branch": branch,
        "capturedAtUtc": utc_now().isoformat(),
        "sourceTreeCleanBeforeRun": not bool(blocking_changes),
        "preexistingLoadEvidence": [
            line[3:] for line in status.splitlines()
            if line.startswith("?? evidencia/ejecuciones/carga-")
        ],
        "profile": args.profile,
        "seed": profile["seed"],
        "durationSecondsPerRepetition": profile["durationSeconds"],
        "concurrency": profile["concurrency"],
        "targetRps": profile["targetRps"],
        "repetitions": profile["repetitions"],
        "operationMix": [{"name": item["name"], "weightPct": item["weight"]} for item in config["operations"]],
        "overall": overall,
        "perOperation": summarize_operations(all_rows, total_elapsed),
        "resourceSummary": summarize_resources(all_resources),
        "slo": evaluate_slo(overall, profile["slo"]),
        "runs": repetitions,
        "limitations": [
            "Laboratorio local de un nodo por motor; no representa capacidad productiva.",
            "Mezcla inicial de lectura segura; no genera goles ni modifica el partido oficial.",
            "docker stats agrega sobrecarga pequena y sus valores se informan como medidos.",
        ],
    }
    with (output_dir / "resultado.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"profile": args.profile, "overall": overall, "slo": result["slo"], "evidence": str(output_dir.relative_to(ROOT))}, ensure_ascii=False, indent=2))
    return 0 if result["slo"].get("passed") is not False else 2


if __name__ == "__main__":
    raise SystemExit(main())
