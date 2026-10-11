# Medición de rendimiento

## Datos de ejecución

- **Fecha:** 10 de octubre de 2026, 22:07:29 UTC-3.
- **Entorno:** local.
- **Procesador:** Intel(R) Core(TM) 5 120U.
- **Núcleos físicos:** 10.
- **Procesadores lógicos:** 12.
- **RAM:** 13,7 GB.
- **API:** `http://127.0.0.1:8000`.

## Método

Se midió el tiempo HTTP extremo a extremo, incluyendo:

- FastAPI y validaciones.
- Middleware.
- Servicio y adaptador.
- Red local.
- Consulta al motor.
- Serialización de la respuesta.

Por cada motor se realizaron:

- 1 solicitud de calentamiento no contabilizada.
- 10 solicitudes medidas.
- Concurrencia igual a 1.
- Timeout de 10 segundos.
- Total de 60 solicitudes medidas.

Esta es una prueba local y secuencial. No representa la capacidad máxima de producción ni una prueba de carga concurrente.

## Resultados

| Motor | Éxito | Promedio ms | Mediana ms | P95 ms | Mínimo ms | Máximo ms |
|---|---:|---:|---:|---:|---:|---:|
| MongoDB | 10/10 | 7,50 | 7,65 | 8,38 | 6,25 | 8,38 |
| Neo4j | 10/10 | 28,68 | 23,32 | 64,76 | 15,37 | 64,76 |
| Cassandra | 10/10 | 16,58 | 15,75 | 27,98 | 11,64 | 27,98 |
| Redis | 10/10 | 6,77 | 6,64 | 7,53 | 6,07 | 7,53 |
| InfluxDB | 10/10 | 27,98 | 28,36 | 63,65 | 15,76 | 63,65 |
| InterSystems IRIS | 10/10 | 53,90 | 50,08 | 75,30 | 41,32 | 75,30 |

## Resultado general

- Solicitudes exitosas: **60/60**.
- Solicitudes fallidas: **0**.
- Promedio general: **23,57 ms**.
- Resultado: **APROBADO**.

Redis y MongoDB presentaron las menores latencias.

IRIS presentó la mayor latencia porque su adaptador establece y cierra una conexión por cada solicitud. Aun así, todos los resultados quedaron ampliamente por debajo del timeout configurado.

Con diez observaciones por motor, el P95 fue calculado mediante rango más cercano. Por eso puede coincidir con el máximo registrado.

## Evidencias vinculadas

| Archivo | Contenido |
|---|---|
| `docs/evidencia/14_rendimiento_api.txt` | Hardware, método y resumen |
| `docs/evidencia/14_rendimiento_api.csv` | 60 mediciones individuales |
| `docs/evidencia/14_rendimiento_api.json` | Resultado estructurado |
| `docs/evidencia/14_rendimiento_api.png` | Captura de ejecución |
| `scripts/medir_rendimiento.py` | Lógica de medición |
| `scripts/medir_rendimiento.ps1` | Ejecución reproducible |
