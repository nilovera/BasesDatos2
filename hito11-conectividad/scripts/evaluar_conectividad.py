"""Orquestador del diagnóstico de conectividad (Hito 11, sección 5.8).

Modos:
    completo  configuración + proceso/resolución/TCP + clientes nativos + API
              y regeneración de docs/matriz_de_conectividad.md
    config    solo la capa de configuración
    tcp       proceso (Docker), resolución y TCP
    nativos   protocolo, autenticación, autorización, contexto y operación
    api       rutas de la API (cadena completa)

Cada modo puede limitarse a un producto (--producto) y no exige que todas
las dependencias estén disponibles a la vez (RNF13).

Ejemplos (desde la raíz del repositorio):
    .venv\\Scripts\\python.exe hito11-conectividad\\scripts\\evaluar_conectividad.py
    .venv\\Scripts\\python.exe hito11-conectividad\\scripts\\evaluar_conectividad.py --modo tcp
    .venv\\Scripts\\python.exe hito11-conectividad\\scripts\\evaluar_conectividad.py --modo nativos --producto neo4j
    .venv\\Scripts\\python.exe hito11-conectividad\\scripts\\evaluar_conectividad.py --set NEO4J_DATABASE=noexiste --etiqueta contexto_incorrecto
"""

from __future__ import annotations

import argparse
import sys
from collections import OrderedDict

import prueba_api
import prueba_clientes_nativos
import prueba_config
import prueba_tcp
from common import (
    ADVERTENCIA,
    BLOQUEADA,
    CAPAS,
    DOCS_DIR,
    FALLA,
    NO_APLICA,
    OK,
    PRODUCTOS,
    SKIP,
    Config,
    Redactor,
    Resultado,
    contexto_ejecucion,
    escribir_evidencia,
    estado_producto,
    imprimir_resultado,
    imprimir_resumen,
    parse_overrides,
    preparar_consola,
)


ABREV = {OK: "OK", FALLA: "FALLA", ADVERTENCIA: "ADV", SKIP: "SKIP", BLOQUEADA: "BLOQ", NO_APLICA: "N/A"}
PRIORIDAD = {FALLA: 0, ADVERTENCIA: 1, OK: 2, NO_APLICA: 3, BLOQUEADA: 4, SKIP: 5}
ORDEN_PRODUCTOS = [p["nombre"] for p in PRODUCTOS.values()]


def celda_capa(items: list[Resultado]) -> str:
    requeridas = [r for r in items if r.requerida] or items
    if not requeridas:
        return "-"
    peor = min(requeridas, key=lambda r: PRIORIDAD.get(r.estado, 9))
    return ABREV.get(peor.estado, peor.estado)


def latencia_operacion(items: list[Resultado]) -> str:
    ops = [r for r in items if r.capa == "operacion" and r.requerida and r.estado in (OK, ADVERTENCIA)]
    return f"{ops[0].duracion_ms:.1f} ms" if ops and ops[0].duracion_ms is not None else "-"


def capa_alcanzada(items: list[Resultado]) -> str:
    ultima = "-"
    for capa in CAPAS:
        req = [r for r in items if r.capa == capa and r.requerida]
        if not req:
            continue
        if all(r.estado in (OK, ADVERTENCIA, NO_APLICA) for r in req):
            ultima = capa
        else:
            break
    return ultima


def generar_matriz(contexto: dict, resultados: list[Resultado], redactar: Redactor) -> str:
    grupos: "OrderedDict[str, list[Resultado]]" = OrderedDict()
    for nombre in ORDEN_PRODUCTOS + ["API Fixture 2030", "Repositorio"]:
        items = [r for r in resultados if r.producto == nombre]
        if items:
            grupos[nombre] = items
    for r in resultados:
        grupos.setdefault(r.producto, [])
        if r not in grupos[r.producto]:
            grupos[r.producto].append(r)

    modulos = {p["nombre"]: p["modulo"] for p in PRODUCTOS.values()}

    lineas = [
        "# Matriz de conectividad",
        "",
        "> Archivo **generado** por `scripts/evaluar_conectividad.py --modo completo`. "
        "No editar a mano: volver a ejecutar el script para actualizarlo.",
        "",
        "## Contexto de la ejecución",
        "",
        "| Campo | Valor |",
        "|---|---|",
    ]
    for clave in ("fecha", "entorno", "origen_de_las_pruebas", "sistema_operativo", "python",
                  "rama", "commit", "timeout_por_prueba_s", "api_base_url", "modo"):
        if clave in contexto:
            lineas.append(f"| {clave.replace('_', ' ')} | {contexto[clave]} |")
    lineas += [
        "",
        "**Significado de OK:** la prueba concreta funcionó en este momento y desde este origen. "
        "No es garantía de rendimiento, escalabilidad ni disponibilidad permanente (RNF17).",
        "",
        "## Estado por dependencia",
        "",
        "| Producto | Módulo | Estado | Última capa superada | Latencia lectura mínima | Ruta principal de la API | Diagnóstico |",
        "|---|---|---|---|---|---|---|",
    ]

    for producto, items in grupos.items():
        if producto == "Repositorio":
            continue
        estado, motivo = estado_producto(items)
        api = [r for r in items if r.capa == "api" and "operación exitosa" in r.prueba]
        api_txt = "-"
        if api:
            status = api[0].detalle.split(";")[0].replace("status=", "HTTP ")
            api_txt = f"{status} ({api[0].clasificacion})"
        lineas.append(
            f"| {producto} | {modulos.get(producto, 'API integrada (Hito 10)')} | **{estado}** | "
            f"{capa_alcanzada(items)} | {latencia_operacion(items)} | {api_txt} | {redactar(motivo)} |"
        )

    capas_tabla = [c for c in CAPAS if any(r.capa == c for r in resultados)]
    lineas += [
        "",
        "## Resultado por capa",
        "",
        "Se muestra el peor resultado de las pruebas **requeridas** de cada capa. "
        "OK = funcionó · FALLA = se intentó y falló · ADV = funcionó con observación · "
        "N/A = la capa no existe en este entorno · BLOQ = no se ejecutó por una falla anterior · "
        "SKIP = no se ejecutó por falta de herramienta o configuración (no significa producto caído).",
        "",
        "| Producto | " + " | ".join(capas_tabla) + " |",
        "|---|" + "---|" * len(capas_tabla),
    ]
    for producto, items in grupos.items():
        if producto == "Repositorio":
            continue
        celdas = [celda_capa([r for r in items if r.capa == c]) for c in capas_tabla]
        lineas.append(f"| {producto} | " + " | ".join(celdas) + " |")

    lineas += ["", "## Detalle de pruebas", ""]
    for producto, items in grupos.items():
        lineas += [
            f"### {producto}",
            "",
            "| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in items:
            dur = f"{r.duracion_ms:.1f} ms" if r.duracion_ms is not None else "-"
            prueba = r.prueba + ("" if r.requerida else " *(complementaria)*")
            detalle = redactar(r.detalle).replace("|", "/")[:300]
            lineas.append(
                f"| {r.capa} | {prueba} | `{redactar(r.objetivo)}` | {r.cliente} | {ABREV.get(r.estado, r.estado)} | "
                f"{r.clasificacion} | {dur} | {detalle} |"
            )
        lineas.append("")

    fallas = [r for r in resultados if r.estado in (FALLA, ADVERTENCIA)]
    lineas += ["## Fallas y observaciones con diagnóstico (RNF10)", ""]
    if not fallas:
        lineas.append("No se registraron fallas ni advertencias en esta ejecución.")
    else:
        lineas += [
            "| Producto | Capa | Prueba | Resultado | Hipótesis | Siguiente paso |",
            "|---|---|---|---|---|---|",
        ]
        for r in fallas:
            lineas.append(
                f"| {r.producto} | {r.capa} | {r.prueba} | {ABREV.get(r.estado)}: {r.clasificacion} | "
                f"{r.hipotesis} | {r.siguiente_paso} |"
            )

    lineas += [
        "",
        "## Evidencia asociada",
        "",
        "- `docs/evidencia/resultados_config.txt` / `.json`",
        "- `docs/evidencia/resultados_tcp.txt` / `.json`",
        "- `docs/evidencia/resultados_clientes.txt` / `.json`",
        "- `docs/evidencia/resultados_api.txt` / `.json` (incluye request ID y línea de log por solicitud)",
        "",
    ]
    return redactar("\n".join(lineas))


def main(argv: list[str] | None = None) -> int:
    preparar_consola()
    parser = argparse.ArgumentParser(
        description="Hito 11 - evaluación de conectividad por capas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--modo", default="completo", choices=["completo", "config", "tcp", "nativos", "api"])
    parser.add_argument("--producto", default="todos", choices=["todos", *PRODUCTOS])
    parser.add_argument("--set", action="append", default=[], metavar="CLAVE=VALOR",
                        help="sobrescribe una variable solo para esta ejecución (escenarios de falla)")
    parser.add_argument("--etiqueta", default="", help="sufijo para no sobrescribir evidencias (ej. antes, durante, despues)")
    parser.add_argument("--sin-escritura", action="store_true", help="no crear la clave diag:hito11:* en Redis")
    parser.add_argument("--cli", action="store_true", help="ejecutar también los CLI nativos dentro de los contenedores")
    parser.add_argument("--desde-contenedor", default="", metavar="CONTENEDOR",
                        help="repetir la prueba TCP desde dentro de un contenedor (RNF3)")
    parser.add_argument("--sin-matriz", action="store_true", help="no regenerar docs/matriz_de_conectividad.md")
    args = parser.parse_args(argv)

    cfg = Config(parse_overrides(args.set))
    redactar = Redactor(cfg.secretos())
    productos = list(PRODUCTOS) if args.producto == "todos" else [args.producto]
    contexto = contexto_ejecucion(cfg, args.modo)
    contexto["api_base_url"] = cfg.get("API_BASE_URL")
    if args.set:
        contexto["overrides"] = ", ".join(k for k in parse_overrides(args.set))

    print("=" * 78)
    print("HITO 11 - EVALUACION DE LA CONECTIVIDAD A LOS PRODUCTOS DEL FIXTURE 2030")
    print("=" * 78)
    for clave in ("fecha", "modo", "entorno", "origen_de_las_pruebas", "commit", "timeout_por_prueba_s"):
        print(f"{clave:>22}: {contexto[clave]}")
    if args.set:
        print(f"{'overrides':>22}: {contexto['overrides']} (valores no mostrados)")
    print()

    todos: list[Resultado] = []
    etapas = []

    if args.modo in ("completo", "config"):
        etapas.append(("1/4 CONFIGURACION", "resultados_config",
                       lambda: prueba_config.evaluar(cfg, productos, redactar), {}))
    if args.modo in ("completo", "tcp"):
        def tcp():
            res = prueba_tcp.evaluar(cfg, productos, redactar, incluir_api=True)
            if args.desde_contenedor:
                res += prueba_tcp.desde_contenedor(cfg, args.desde_contenedor, productos, redactar)
            return res
        etapas.append(("2/4 PROCESO, RESOLUCION Y TCP", "resultados_tcp", tcp, {}))
    if args.modo in ("completo", "nativos"):
        etapas.append(("3/4 CLIENTES NATIVOS", "resultados_clientes",
                       lambda: prueba_clientes_nativos.evaluar(cfg, productos, redactar,
                                                               not args.sin_escritura, args.cli), {}))
    if args.modo in ("completo", "api"):
        etapas.append(("4/4 API INTEGRADA", "resultados_api", None, {}))

    for titulo, nombre, fn, _ in etapas:
        print(f"--- {titulo} " + "-" * max(0, 70 - len(titulo)))
        extra = None
        if nombre == "resultados_api":
            resultados, registros = prueba_api.evaluar(cfg, redactar)
            extra = {"solicitudes": registros}
        else:
            resultados = fn()
        for r in resultados:
            imprimir_resultado(r)
        txt, _ = escribir_evidencia(nombre, contexto, resultados, redactar, args.etiqueta, extra)
        print(f"    evidencia: {txt.relative_to(DOCS_DIR.parent)}")
        print()
        todos += resultados

    imprimir_resumen(todos)

    if args.modo == "completo" and not args.sin_matriz:
        sufijo = f"_{args.etiqueta}" if args.etiqueta else ""
        destino = DOCS_DIR / f"matriz_de_conectividad{sufijo}.md"
        destino.write_text(generar_matriz(contexto, todos, redactar), encoding="utf-8")
        print(f"\nMatriz regenerada: {destino.relative_to(DOCS_DIR.parent)}")

    return 1 if any(r.estado == FALLA and r.requerida for r in todos) else 0


if __name__ == "__main__":
    sys.exit(main())
