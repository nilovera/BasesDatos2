# Hito 12 — Data Mart y evaluación de rendimiento

## Hipótesis y método

Separar agregaciones analíticas del núcleo operacional puede reducir competencia
por recursos y aprovechar un grano de consulta específico. El costo es almacenar
copias y aceptar frescura dependiente del ETL. La hipótesis se evalúa mediante
resultados equivalentes, latencia, throughput, errores y recursos, sin declarar
una mejora solo por utilizar otro motor.

```text
powershell -ExecutionPolicy Bypass -File scripts\comparar_rendimiento_datamart.ps1 -Iteraciones 100
```

## Comparaciones registradas

La [línea base sin pool](../../evidencia/ejecuciones/rendimiento-datamart-20261125T182329Z/resultado.json)
corresponde al commit `a279c62cf4804142685e9a8ec594f6ab1da75174`.
La [ejecución con pool](../../evidencia/ejecuciones/rendimiento-datamart-20261125T192824Z/resultado.json)
corresponde a `70dc0d9c424d334122e49f85055e19b3f95c4d0d`.
Cada una realizó 100 consultas por alternativa sobre un partido, con igualdad
de resultados y cero errores.

| Ejecución y camino | p50 | p95 | p99 | Throughput |
|---|---:|---:|---:|---:|
| Base operacional | 11,117 ms | 21,554 ms | 26,283 ms | 74,688 req/s |
| Data Mart sin pool | 18,555 ms | 28,853 ms | 45,378 ms | 48,661 req/s |
| Segunda ejecución operacional | 26,394 ms | 46,363 ms | 67,644 ms | 35,056 req/s |
| Data Mart con pool | 12,146 ms | 23,143 ms | 39,311 ms | 71,949 req/s |

La primera comparación fue desfavorable al Data Mart. El cambio de conexiones
por solicitud a un pool acotado de 2–10 busca reducir ese costo. Entre los dos
registros del Data Mart, p95 disminuyó 19,79 % y throughput aumentó 47,86 %.
Son diferencias observadas entre ejecuciones; no aíslan todos los factores de
variación. Dentro de la segunda ejecución, el p95 Data Mart fue 50,08 % menor
que el operacional.

## Carga mixta y recursos

Los perfiles de lectura posteriores ya se ejecutaron y conservaron muestras de
CPU/memoria; no corresponden a una tarea de ejecución pendiente.

| Perfil | Consultas Data Mart y p95 | Consultas operacionales y p95 |
|---|---|---|
| Normal | 510; 26,034 ms | 348; 35,937 ms |
| Estrés | 756; 42,158 ms | 470; 62,494 ms |

La mezcla asigna pesos distintos a ambos endpoints. Sus cantidades y tasas no
se interpretan como capacidad individual ni como prueba causal del pool. Los
percentiles son observaciones bajo la carga del sistema completo.

## Conclusión y límites

Existe evidencia cuantitativa de las comparaciones y de ambos endpoints bajo
carga. El pool es una mejora técnica implementada y la segunda comparación
resultó favorable; no se declara una ventaja universal o a gran volumen.
Para generalizar se necesita más volumen, condiciones comparables, repeticiones
y análisis del costo de frescura y de ETL.

El refresh usa UPSERT y no elimina de forma general hechos ausentes en snapshots
posteriores. La reconciliación de correcciones después de una carga ya
materializada requiere tratamiento específico. La idempotencia de carga idéntica
no acredita por sí sola esa reconciliación.

Evidencias y contexto: [estado de validación](../estado_validacion.md).
