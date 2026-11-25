# Pruebas de carga, SLI, SLO y límites

## Objetivo

Medir la cadena `cliente -> API -> almacén -> respuesta` con una mezcla estable
de consultas sobre MongoDB/Redis, Cassandra, InfluxDB, Neo4j y PostgreSQL. El
simulador no reemplaza pruebas nativas de cada motor: permite observar el flujo
que experimenta un usuario real y correlacionarlo con recursos.

## Perfiles reproducibles

| Perfil | Semilla | Duración | Concurrencia | Tasa objetivo | Repeticiones | Propósito |
|---|---:|---:|---:|---:|---:|---|
| Humo | 2029 | 15 s | 2 | 2 req/s | 1 | Detectar fallas básicas con carga mínima |
| Normal | 2030 | 60 s | 12 | 20 req/s | 3 | Medir demanda esperada y variabilidad |
| Estrés | 2031 | 60 s | 40 | 80 req/s | 1 | Superar la demanda y buscar degradación |

La mezcla es de lectura segura: partido y caché, comentarios, posiciones y mapa
de calor, grafo, consulta operacional y Data Mart. Los pesos suman 100 y están
versionados en `config/carga/perfiles.json`. El warm-up queda fuera de la
medición. Cada repetición conserva todas las solicitudes y muestras de
`docker stats` para API y almacenes.

## SLI y objetivos iniciales

Los siguientes valores son **SLO internos de laboratorio**, no SLA contractual:

| SLI | Humo | Tráfico normal | Estrés |
|---|---:|---:|---|
| Tasa de error | 0 % | <= 1 % | Medir límite |
| Latencia p95 | <= 750 ms | <= 500 ms | Medir degradación |
| Latencia p99 | <= 1.500 ms | <= 1.000 ms | Medir cola |

El SLA requiere un acuerdo externo, consecuencias y una ventana prolongada de
disponibilidad. No se inventa a partir de una ejecución local. Después de medir
se revisarán estos SLO y se definirán alertas que avisen antes de incumplirlos.

## Ejecución

El simulador exige que código y configuración estén versionados para vincular
la evidencia al commit. Permite carpetas `carga-*` generadas previamente por el
mismo flujo, de modo que los tres perfiles puedan ejecutarse en secuencia:

```text
powershell -ExecutionPolicy Bypass -File scripts\probar_carga.ps1 -Perfil humo
powershell -ExecutionPolicy Bypass -File scripts\probar_carga.ps1 -Perfil normal
powershell -ExecutionPolicy Bypass -File scripts\probar_carga.ps1 -Perfil estres
```

También puede ejecutarse `-Perfil todos`. Los resultados quedan en
`evidencia/ejecuciones/carga-<perfil>-<UTC>/`:

- `resultado.json`: percentiles, throughput, errores, recursos, SLO y commit;
- `solicitudes-rep-XX.csv`: resultado individual por request;
- `recursos-rep-XX.csv`: CPU, memoria, red, disco y procesos por contenedor.

## Interpretación y limitaciones

La tasa objetivo no es throughput garantizado: si la API se satura, el trabajo
se acumula y el throughput logrado baja. Estrés no falla por superar un SLO;
busca localizar el límite. Después debe ejecutarse nuevamente humo para medir
recuperación.

Esta primera mezcla no genera goles, asistencias ni comentarios nuevos. Es una
decisión deliberada para no modificar el partido oficial durante una medición
comparativa. Las escrituras sintéticas se incorporarán como escenario separado,
con IDs e idempotencia reproducibles.
