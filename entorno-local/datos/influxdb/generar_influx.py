"""Genera los puntos del Hito 8 (InfluxDB) en line protocol.

Reproduce exactamente el generador original del grupo
(fixture2030-influxdb/scripts/generar_datos.ps1 y agregacion.ps1), pero en
Python para que el separador decimal no dependa de la configuración regional
de Windows (en es-AR, PowerShell escribe "50,23" y el line protocol lo rechaza).

Salida (carpeta generado/, montada en el contenedor como /datos/generado):
  - estadisticas_equipo.lp : 1.080 puntos, 2 equipos, 1 punto cada 10 s, 90 min
  - resumen_15m.lp         : 12 resúmenes de 15 minutos (downsampling)
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

SALIDA = Path(__file__).resolve().parent / "generado"
INICIO = datetime(2030, 6, 13, 20, 0, 0, tzinfo=timezone.utc)
PARTIDO = "PAR-0001"


def generar() -> list[tuple[int, str, float, int, int]]:
    puntos = []
    for i in range(540):
        ts = int((INICIO + timedelta(seconds=i * 10)).timestamp())
        pos_arg = 50 + round(8 * math.sin(i / 35), 2)
        pos_mex = round(100 - pos_arg, 2)
        puntos.append((ts, "ARG", pos_arg, 1 + (i % 4), i // 45))
        puntos.append((ts, "MEX", pos_mex, 1 + ((i + 2) % 4), i // 60))
    return puntos


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    puntos = generar()

    detalle = [
        f"estadisticas_equipo,partido_id={PARTIDO},equipo_id={eq} "
        f"posesion_pct={pos!r},pases_intervalo={pases}i,tiros_acumulados={tiros}i {ts}"
        for ts, eq, pos, pases, tiros in puntos
    ]
    (SALIDA / "estadisticas_equipo.lp").write_text("\n".join(detalle) + "\n", encoding="utf-8", newline="\n")

    ventanas: dict[tuple[int, str], list[tuple[float, int]]] = {}
    inicio_ts = int(INICIO.timestamp())
    for ts, eq, pos, pases, _ in puntos:
        ventana = inicio_ts + ((ts - inicio_ts) // 900) * 900
        ventanas.setdefault((ventana, eq), []).append((pos, pases))

    resumen = []
    for (ventana, eq), valores in sorted(ventanas.items()):
        promedio = round(sum(v[0] for v in valores) / len(valores), 2)
        pases = sum(v[1] for v in valores)
        resumen.append(
            f"resumen_equipo_minuto,partido_id={PARTIDO},equipo_id={eq} "
            f"posesion_promedio={promedio!r},pases_total={pases}i,muestras={len(valores)}i,"
            f"ventana_inicio_ms={ventana * 1000}i,ventana_fin_ms={(ventana + 900) * 1000}i {ventana}"
        )
    (SALIDA / "resumen_15m.lp").write_text("\n".join(resumen) + "\n", encoding="utf-8", newline="\n")

    print(f"detalle: {len(detalle)} puntos | resumen: {len(resumen)} filas | carpeta: {SALIDA}")


if __name__ == "__main__":
    main()
