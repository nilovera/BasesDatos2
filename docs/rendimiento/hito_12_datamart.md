# Hito 12 — Data Mart y mejora de rendimiento

## Hipótesis

Las agregaciones históricas repetidas sobre datos operacionales competirán con el
camino transaccional. Una estrella indexada y precalculada debería reducir la
latencia de cola y estabilizar el throughput analítico a cambio de almacenamiento
duplicado y frescura eventual.

## Protocolo reproducible

1. Fijar commit, equipo, versiones, seed, volumen, concurrencia y duración.
2. Ejecutar la consulta operacional y registrar p50/p95/p99, throughput, errores,
   CPU y memoria.
3. Identificar el cuello de botella con esos datos.
4. Ejecutar el ETL al Data Mart.
5. Repetir exactamente la misma carga contra la consulta analítica.
6. Comparar cuantitativamente y documentar el trade-off de frescura/costo.

Comando de línea base:

```text
powershell -ExecutionPolicy Bypass -File scripts\comparar_rendimiento_datamart.ps1 -Iteraciones 100
```

## Estado

### Línea base `2260cad`

Con 100 iteraciones, un partido y cuatro hechos, ambos caminos devolvieron el
mismo resultado y cero errores:

| Camino | p50 | p95 | p99 | Throughput |
|---|---:|---:|---:|---:|
| Operacional | 11,117 ms | 21,554 ms | 26,283 ms | 74,688 req/s |
| Data Mart sin pool | 18,555 ms | 28,853 ms | 45,378 ms | 48,661 req/s |

La línea base no demostró mejora: permitió identificar que abrir una conexión
PostgreSQL en cada solicitud dominaba una consulta sobre apenas cuatro filas.

### Cambio técnico aislado

Se reemplazó la conexión por solicitud por un `ConnectionPool` de tamaño 2–10.
No se cambió el SQL, los datos, el endpoint ni el script de 100 iteraciones. La
prueba se repitió sobre el commit `70dc0d9`, con resultados equivalentes y cero
errores:

| Camino | p50 | p95 | p99 | Throughput |
|---|---:|---:|---:|---:|
| Operacional | 26,394 ms | 46,363 ms | 67,644 ms | 35,056 req/s |
| Data Mart con pool | 12,146 ms | 23,143 ms | 39,311 ms | 71,949 req/s |

Frente al Data Mart sin pool, la optimización redujo p50 un 34,54 %, p95 un
19,79 % y p99 un 13,37 %, y aumentó el throughput un 47,86 %. Dentro de la misma
ejecución, el Data Mart obtuvo p50 53,98 % menor, p95 50,08 % menor, p99 41,89 %
menor y throughput 105,24 % mayor que el camino operacional.

Esta comparación demuestra el efecto del pool bajo la línea base funcional,
pero no aísla la variabilidad entre ejecuciones ni prueba comportamiento con
volumen, concurrencia o presión de recursos. La validación completa del Hito 12
continúa pendiente hasta incorporar los perfiles de humo, tráfico normal y
estrés, medir CPU/memoria y repetir cada escenario varias veces.

