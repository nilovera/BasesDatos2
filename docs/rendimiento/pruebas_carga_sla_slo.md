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

## Resultados medidos — commit `3f7e488`

Las ejecuciones del 25 de noviembre de 2026 produjeron los siguientes valores:

| Escenario | Requests | Errores | p50 | p95 | p99 | Throughput | Evaluación |
|---|---:|---:|---:|---:|---:|---:|---|
| Humo con `localhost` | 30 | 0 | 2.066,134 ms | 2.105,750 ms | 2.109,771 ms | 0,954 req/s | No cumple |
| Humo corregido | 30 | 0 | 20,937 ms | 48,234 ms | 52,833 ms | 2,063 req/s | Cumple |
| Normal, tres repeticiones | 3.600 | 0 | 18,050 ms | 34,926 ms | 46,605 ms | 19,998 req/s | Cumple |
| Estrés | 4.800 | 0 | 22,305 ms | 55,110 ms | 78,080 ms | 79,932 req/s | Informativo |
| Humo posterior | 30 | 0 | 18,491 ms | 38,819 ms | 45,311 ms | 2,062 req/s | Cumple |

La primera prueba permitió aislar una demora de resolución de `localhost` en el
cliente Python sobre Windows. Cambiar únicamente el destino a `127.0.0.1`
redujo p95 un 97,71 % y elevó el throughput un 116,25 % con la misma carga.

En tráfico normal las tres repeticiones sostuvieron 20 req/s. Un máximo aislado
de 1.690,769 ms correspondió a una recomendación de Neo4j durante la primera
repetición; las dos siguientes obtuvieron p99 de 42,273 y 46,189 ms. Se registra
como calentamiento o pausa transitoria, no como degradación sostenida.

Estrés multiplicó por cuatro la tasa normal. La API y Neo4j fueron los puntos de
mayor presión: ambos promediaron alrededor de 64,6 % de CPU y Neo4j alcanzó un
pico multihilo de 210,89 %. `grafo_recomendaciones` tuvo el mayor p95 por
operación, 72,527 ms. Redis y PostgreSQL conservaron bajo consumo; Cassandra
mantuvo aproximadamente 1,1 GiB de memoria, esperable para su JVM local.

No hubo errores, pérdida de throughput ni saturación a 80 req/s. Por lo tanto,
la capacidad **demostrada** del laboratorio es al menos 80 req/s, pero su límite
máximo no fue determinado. El humo posterior cumplió todos los SLO y todas las
dependencias quedaron `UP`, demostrando recuperación después del estrés.

Evidencias relacionadas:

- `carga-humo-20261125T230156Z`: diagnóstico con `localhost`;
- `carga-humo-20261125T231123Z`: humo corregido;
- `carga-normal-20261125T231315Z`: tres repeticiones normales;
- `carga-estres-20261125T232053Z`: estrés;
- `carga-humo-20261125T232154Z`: recuperación.
