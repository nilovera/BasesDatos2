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

El modelo, ETL, equivalencia funcional, persistencia, métricas y script de
comparación están implementados. La prueba con volumen, concurrencia y recursos
se mantiene pendiente hasta incorporar el simulador de humo/normal/estrés. Por
lo tanto todavía no se afirma una mejora porcentual.

