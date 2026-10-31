"""Verifica que los datos de laboratorio de las seis bases estén intactos (RNF5 / RNF11).

Reutiliza el catálogo del Hito 12 (datos-o-generadores/catalogo_claves.json), que guarda la
"huella" (SHA-256 del JSON canónico) de cada respuesta correcta de la API. Para cada base toma
una muestra fija de claves, las consulta por la API y compara la huella con la del catálogo.

- Si todas coinciden: la base tiene exactamente los mismos datos que el 24/10 (Hito 12), es decir,
  ni la instrumentación ni las pruebas de falla alteraron datos funcionales.
- Si una base devuelve 200 pero con otra huella o vacía: posible volumen montado vacío
  (ver docs/limitaciones_y_evidencia.md, caso IRIS/WSL).

Antes de comparar se recrean las sesiones sintéticas SES-H12-* de Redis (vencen a las 4 h; se
regeneran idénticas porque usan la misma semilla).

Uso: .venv\\Scripts\\python.exe fixture2030-hito-13-monitoreo\\scripts\\verificar_datos.py --momento antes
Guarda evidencia/resultados_sin_secretos/integridad_datos_<momento>.json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict

import httpx

import comun_monitoreo as cm

HITO12_SCRIPTS = cm.API_ROOT / "fixture2030-hito-12-carga-optimizacion" / "scripts"
MUESTRA_POR_BASE = 15


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--momento", default="control", help="antes | despues | control")
    args = ap.parse_args()

    sys.path.insert(0, str(HITO12_SCRIPTS))
    import comun as comun_h12  # noqa: WPS433  (huella del Hito 12)
    import preparar_datos  # noqa: WPS433

    catalogo = json.loads(comun_h12.CATALOGO_PATH.read_text(encoding="utf-8"))
    por_tipo: dict[str, list[dict]] = defaultdict(list)
    for e in catalogo["claves"]:
        if e.get("determinista") and e.get("huella"):
            por_tipo[e["tipo"]].append(e)

    try:
        sesiones = preparar_datos.preparar_redis()
    except Exception as error:  # noqa: BLE001
        sesiones = f"error {type(error).__name__}"

    rng = random.Random(2030)            # muestra fija: siempre las mismas claves
    resultado = {}
    print(f"=== HITO 13 - INTEGRIDAD DE DATOS ({args.momento}) ===")
    print(f"Catálogo de referencia: Hito 12, {catalogo['resumen']['fecha']} | sesiones Redis: {sesiones}")
    with httpx.Client(base_url=cm.API, timeout=15) as cliente:
        for tipo, claves in sorted(por_tipo.items()):
            muestra = rng.sample(claves, min(MUESTRA_POR_BASE, len(claves)))
            iguales, distintas, errores = 0, [], []
            for e in muestra:
                try:
                    r = cliente.get(e["url"])
                except httpx.HTTPError as error:
                    errores.append(f"{e['clave']}: {type(error).__name__}")
                    continue
                if r.status_code != 200:
                    errores.append(f"{e['clave']}: HTTP {r.status_code}")
                elif comun_h12.huella(r.json()) == e["huella"]:
                    iguales += 1
                else:
                    distintas.append(e["clave"])
            motor = muestra[0]["motor"] if muestra else tipo
            resultado[motor] = {"claves_verificadas": len(muestra), "huella_igual": iguales,
                                "huella_distinta": distintas, "errores": errores,
                                "estado": "intacto" if iguales == len(muestra) else "revisar"}
            print(f"  {motor:<18} {iguales}/{len(muestra)} respuestas idénticas al catálogo"
                  + (f" | distintas: {distintas[:3]}" if distintas else "") + (f" | errores: {errores[:3]}" if errores else ""))

    datos = {"fecha": cm.ahora_iso(), "momento": args.momento, "commit": cm.commit_actual(),
             "referencia": f"catalogo_claves.json del Hito 12 ({catalogo['resumen']['fecha']})",
             "metodo": "SHA-256 del JSON canónico de la respuesta de la API (sin campos volátiles como el TTL)",
             "por_base": resultado}
    cm.escribir_json(cm.RESULTADOS_DIR / f"integridad_datos_{args.momento}.json", datos)
    todo_ok = all(v["estado"] == "intacto" for v in resultado.values())
    print("\nResultado:", "todas las bases intactas" if todo_ok else "hay bases para revisar")
    print(f"Evidencia: evidencia/resultados_sin_secretos/integridad_datos_{args.momento}.json")
    return 0 if todo_ok else 2


if __name__ == "__main__":
    sys.exit(main())
