"""Genera y verifica el catálogo común sin conectarse a ninguna base de datos."""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "fuentes" / "catalogo_base.json"
DESTINATION = ROOT / "data" / "catalogo"
POSITIONS = {"Arquero", "Defensor", "Mediocampista", "Delantero"}
STATES = {"PROGRAMADO", "EN_CURSO", "SUSPENDIDO", "FINALIZADO", "CANCELADO"}


def serialize(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def generate(source: dict) -> dict[str, object]:
    teams = []
    players = []
    counters: Counter = Counter()
    number = 1
    for index, selection in enumerate(source["selecciones"], start=1):
        team_id = f"EQ-{index:02d}"
        teams.append({
            "_id": team_id,
            "nombre": selection["nombre"],
            "confederacion": selection["confederacion"],
            "ranking": index,
        })
        profile_key = selection["perfil"]
        profile = source["perfiles_nombres"][profile_key]
        for position in source["posiciones_plantel"]:
            combination = counters[profile_key] * 17 % 256
            full_name = (
                profile["nombres"][combination % 16]
                + " "
                + profile["apellidos"][combination // 16]
            )
            birth = datetime(
                1993 + number * 7 % 19,
                1 + number * 5 % 12,
                1 + number * 11 % 28,
                tzinfo=timezone.utc,
            )
            players.append({
                "_id": f"JUG-{number:04d}",
                "nombre": full_name,
                "fecha_nacimiento": birth.isoformat().replace("+00:00", "Z"),
                "posicion": position,
                "equipo_id": team_id,
            })
            counters[profile_key] += 1
            number += 1
    return {
        "equipos": teams,
        "jugadores": players,
        "equivalencias_codigos": copy.deepcopy(source["equivalencias_codigos"]),
        "partidos": copy.deepcopy(source["partidos"]),
        "eventos": copy.deepcopy(source["eventos"]),
    }


def _index(rows: list[dict], pattern: str, label: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        identifier = row.get("_id", "")
        if not isinstance(identifier, str) or not re.fullmatch(pattern, identifier):
            raise ValueError(f"Formato de ID inválido en {label}: {identifier!r}")
        if identifier in result:
            raise ValueError(f"ID duplicado en {label}: {identifier}")
        result[identifier] = row
    return result


def _utc(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Fecha inválida: {value!r}") from exc
    if parsed.tzinfo is None or not value.endswith("Z"):
        raise ValueError(f"La fecha debe incluir UTC con sufijo Z: {value!r}")


def validate(catalog: dict[str, object]) -> None:
    teams = _index(catalog["equipos"], r"EQ-\d{2}", "equipos")
    players = _index(catalog["jugadores"], r"JUG-\d{4}", "jugadores")
    matches = _index(catalog["partidos"], r"PAR-\d{4}", "partidos")
    events = _index(catalog["eventos"], r"EVE-\d{6}", "eventos")
    if len(teams) != 64 or len(players) != 1024:
        raise ValueError("El catálogo de laboratorio requiere 64 equipos y 1.024 jugadores")
    names = set()
    counts: Counter = Counter()
    for player in players.values():
        if player["equipo_id"] not in teams:
            raise ValueError(f"Jugador huérfano: {player['_id']}")
        if player["posicion"] not in POSITIONS:
            raise ValueError(f"Posición inválida: {player['_id']}")
        if player["nombre"] in names:
            raise ValueError("El dataset sintético contiene nombres duplicados")
        names.add(player["nombre"])
        counts[player["equipo_id"]] += 1
        _utc(player["fecha_nacimiento"])
    if any(counts[team_id] != 16 for team_id in teams):
        raise ValueError("Cada equipo de laboratorio debe tener 16 jugadores")
    for code, team_id in catalog["equivalencias_codigos"].items():
        if not re.fullmatch(r"[A-Z]{3}", code) or team_id not in teams:
            raise ValueError(f"Equivalencia de equipo inválida: {code}")
    for match in matches.values():
        home, away = match["equipo_local_id"], match["equipo_visitante_id"]
        if home not in teams or away not in teams or home == away:
            raise ValueError(f"Participantes inválidos: {match['_id']}")
        if match["estado"] not in STATES:
            raise ValueError(f"Estado de partido inválido: {match['_id']}")
        _utc(match["inicio_programado"])
    for event in events.values():
        if event.get("partido_id") not in matches:
            raise ValueError(f"Evento de partido inexistente: {event['_id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verificar sin escribir archivos")
    args = parser.parse_args()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    catalog = generate(source)
    validate(catalog)
    if not args.check:
        DESTINATION.mkdir(parents=True, exist_ok=True)
    for name, values in catalog.items():
        path = DESTINATION / f"{name}.json"
        expected = serialize(values)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Catálogo desactualizado: {path.relative_to(ROOT)}")
        else:
            path.write_text(expected, encoding="utf-8", newline="\n")
    print("OK: 64 equipos, 1.024 jugadores, referencias válidas y catálogo reproducible.")
    print(f"Partidos de demostración: {len(catalog['partidos'])}; eventos iniciales: {len(catalog['eventos'])}.")


if __name__ == "__main__":
    main()
