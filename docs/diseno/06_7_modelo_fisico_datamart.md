# 6.7 — Modelo físico del Data Mart

## Objetivo y frontera

El Data Mart separa las consultas analíticas del camino operacional. MongoDB
continúa siendo la fuente oficial y InfluxDB conserva series temporales; PostgreSQL
recibe una proyección por lote con atraso controlado. Si PostgreSQL falla, no se
bloquean eventos, comentarios, telemetría ni lecturas del fixture.

## Esquema estrella y granos

No se mezclan métricas de granularidad diferente:

| Tabla | Grano | Medidas |
|---|---|---|
| `fact_evento_partido` | Un evento oficial efectivo | goles, asistencias |
| `fact_estadistica_equipo_15m` | Un partido, equipo y ventana de 15 minutos | posesión, pases, tiros, goles, muestras |

Dimensiones conformadas: fecha, torneo, partido, equipo, jugador y tipo de evento.
Las claves naturales (`EQ-xx`, `JUG-xxxx`, `PAR-xxxx`, `EVE-xxxxxx`) quedan como
atributos únicos y las relaciones internas usan claves sustitutas.

## ETL idempotente

`POST /api/v1/analitica/datamart/refrescar` toma un corte de MongoDB, resuelve
correcciones antes de proyectar y toma los resúmenes de 15 minutos de InfluxDB.
Todas las dimensiones y hechos usan `ON CONFLICT`; repetir el lote converge sin
duplicar. `etl_ejecucion` registra inicio, fin, estado y cantidades.

La carga es deliberadamente batch. El costo es que la analítica puede estar
atrasada hasta el siguiente refresh; el beneficio es aislar la escritura oficial
y poder reconstruir la proyección.

## Comparación exigida por Hito 12

Los endpoints operacional y analítico responden la misma pregunta, goles por
equipo. `comparar_rendimiento_datamart.ps1` ejecuta el mismo número de solicitudes
y calcula p50, p95 y p99. Con el único partido actual constituye solamente una
línea base funcional. La mejora se declarará demostrada después de cargar el
dataset sintético de volumen, fijar concurrencia y duración, guardar recursos y
errores, y comparar antes/después bajo idénticas condiciones.

## Seguridad, persistencia y límites

- PostgreSQL escucha solo en `127.0.0.1:5433`.
- La contraseña local se monta mediante secreto y no se versiona.
- El volumen nombrado conserva el esquema y los hechos.
- La API académica aún no tiene autorización; por eso el endpoint de refresh no
  debe exponerse fuera del laboratorio.
- Un único contenedor no demuestra alta disponibilidad ni recuperación regional.

