# Data Mart analítico

PostgreSQL contiene una proyección analítica separada del camino operacional. El esquema
`analytics` usa dimensiones conformadas y dos hechos con granos distintos:

- `fact_evento_partido`: un evento oficial efectivo por fila.
- `fact_estadistica_equipo_15m`: un equipo, un partido y una ventana de 15 minutos por fila.

La carga se ejecuta desde `POST /api/v1/analitica/datamart/refrescar`. Usa `UPSERT`, por lo
que repetir exactamente la misma carga no duplica hechos. MongoDB e InfluxDB continúan siendo
las fuentes operacionales; PostgreSQL admite atraso controlado y nunca participa de la
confirmación de un evento oficial.

La contraseña se genera localmente en `.secretos/datamart-password.txt`, no se versiona y
se monta como secreto de Docker.

