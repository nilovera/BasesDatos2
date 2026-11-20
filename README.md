# Fixture 2030 - Hito 6: Comentarios masivos en Cassandra

## 1. Descripción

Este módulo implementa la persistencia de comentarios masivos del Fixture 2030 mediante Apache Cassandra. El diseño parte de patrones de consulta conocidos y está preparado para escrituras intensivas y lecturas acotadas por partido, usuario y tiempo.

La solución utiliza dos tablas:

- `comentarios_por_partido`: comentarios recientes o ventanas temporales de un partido.
- `comentarios_por_usuario`: historial reciente de un usuario sin filtrar la tabla principal.

Cada comentario se almacena en ambas tablas mediante duplicación controlada. La primera utiliza buckets de diez minutos y la segunda utiliza buckets diarios para evitar particiones ilimitadas.

## 2. Relación con los hitos anteriores

- MongoDB conserva los datos descriptivos y flexibles de equipos y jugadores.
- Neo4j representa las relaciones entre equipos, jugadores, partidos, sedes y eventos.
- Cassandra incorpora el flujo masivo de comentarios asociados a los partidos.

Los identificadores `PAR-0001` a `PAR-0096` mantienen la referencia lógica con los 96 partidos construidos en el Hito 5.

## 3. Estructura del módulo

```text
fixture2030-cassandra/
├── docker-compose.yml
├── scripts/
│   ├── esquema.cql
│   ├── carga_muestra.cql
│   ├── crud.cql
│   ├── consultas.cql
│   ├── carga_o_prueba.ps1
│   └── carga_masiva.cql
├── data/
├── docs/
│   ├── patrones_de_acceso.md
│   ├── modelo_tabular.md
│   ├── decisiones_de_particionamiento.md
│   ├── rendimiento.md
│   └── evidencia/
└── README.md
```

La carpeta `data` recibe los CSV producidos por el generador. Los archivos masivos no necesitan almacenarse en el repositorio porque pueden reproducirse con `carga_o_prueba.ps1` y cada uno supera los 150 MB.

## 4. Requisitos previos

- Docker Desktop iniciado.
- Docker Compose disponible.
- PowerShell.
- Puerto local `9042` disponible.

El ambiente utiliza la imagen oficial declarada como `cassandra:latest`.

## 5. Iniciar el ambiente

Abrir PowerShell y ubicarse en la carpeta del proyecto:

```powershell
Set-Location C:\fixture2030-cassandra
```

Crear e iniciar el contenedor:

```powershell
docker compose up -d
docker compose ps
```

El primer inicio puede tardar mientras se descarga la imagen y Cassandra prepara el nodo.

Verificar el estado:

```powershell
docker exec -it fixture2030-cassandra nodetool status
```

La salida esperada debe mostrar `UN`, que significa `Up/Normal`.

Consultar la versión:

```powershell
docker exec -it fixture2030-cassandra cqlsh
```

Dentro de `cqlsh`:

```sql
SHOW VERSION;
EXIT;
```

En la ejecución documentada se observó Cassandra 5.0.9 y cqlsh 6.2.0. Como se utiliza `latest`, la versión puede cambiar en ejecuciones posteriores y debe registrarse nuevamente.

## 6. Crear el esquema

Ejecutar:

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/esquema.cql
```

El script crea:

- Keyspace `fixture2030_comentarios`.
- Tabla principal `comentarios_por_partido`.
- Tabla secundaria `comentarios_por_usuario`.

El laboratorio utiliza `SimpleStrategy` y factor de replicación 1 porque posee un solo nodo. Esta configuración no representa alta disponibilidad.

### Comprobar la idempotencia del esquema

Ejecutar el mismo comando una segunda vez:

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/esquema.cql
```

La segunda ejecución debe finalizar sin errores y mostrar nuevamente un único keyspace con las mismas dos tablas. Las cláusulas `IF NOT EXISTS` evitan duplicar las estructuras.

## 7. Ejecutar la carga de muestra

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/carga_muestra.cql
```

Resultados esperados:

| Verificación | Cantidad |
|---|---:|
| `PAR-0001`, bucket `203006132000` | 6 |
| `PAR-0001`, bucket `203006132010` | 3 |
| `PAR-0002`, bucket `203006141800` | 3 |
| `USR-0001`, día `20300613` | 2 |

### Comprobar la idempotencia de la muestra

Ejecutar `carga_muestra.cql` por segunda vez:

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/carga_muestra.cql
```

Las cantidades deben permanecer en `6`, `3`, `3` y `2`. Los UUID, timestamps y claves son fijos, por lo que Cassandra realiza upsert sobre las mismas filas y no crea duplicados.

Esta doble ejecución constituye la evidencia explícita de idempotencia de la carga de prueba.

## 8. Ejecutar las consultas

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/consultas.cql
```

El archivo demuestra:

1. Seis comentarios recientes de `PAR-0001`, ordenados del más reciente al más antiguo.
2. Tres comentarios de una ventana temporal dentro de un bucket conocido.
3. Dos comentarios del historial de `USR-0001` mediante la tabla secundaria.

Todas las consultas utilizan claves de partición compatibles con el esquema. No se utiliza `ALLOW FILTERING`.

## 9. Ejecutar las operaciones CRUD

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/crud.cql
```

El script realiza y comprueba:

1. `INSERT` del mismo comentario en las dos tablas.
2. `SELECT` de la fila insertada con estado `pendiente` y cero likes.
3. `UPDATE` a estado `visible` y diez likes en ambas representaciones.
4. `DELETE` mediante las claves completas.
5. Dos consultas finales con `0 rows`.

La actualización y la eliminación deben aplicarse a las dos tablas porque existe duplicación controlada.

## 10. Validar el mecanismo de carga masiva

Antes del volumen completo puede generarse una prueba de 1.000 comentarios:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\carga_o_prueba.ps1" -Cantidad 1000
```

Salida esperada:

```text
Comentarios únicos generados: 1000
Filas físicas preparadas: 2000
Partidos utilizados: 96
Usuarios posibles: 50000
```

Cargar los archivos de prueba:

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/carga_masiva.cql
```

Las dos operaciones `COPY` deben importar 1.000 filas con `0 skipped`. La partición de verificación debe devolver 11 filas.

## 11. Generar más de un millón de comentarios

El generador utiliza por defecto 1.000.128 comentarios:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\carga_o_prueba.ps1"
```

Salida esperada para la cantidad:

```text
Comentarios únicos generados: 1000128
Filas físicas preparadas: 2000256
Partidos utilizados: 96
Usuarios posibles: 50000
```

La misma cantidad puede indicarse explícitamente:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\carga_o_prueba.ps1" -Cantidad 1000128
```

El script reemplaza los CSV anteriores y genera nuevamente las mismas claves. Esto permite repetir el conjunto sin producir identificadores distintos.

## 12. Ejecutar la carga masiva y la medición

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/carga_masiva.cql
```

En la ejecución documentada se obtuvieron los siguientes resultados:

| Tabla | Filas | Tiempo | Tasa promedio | Omitidas |
|---|---:|---:|---:|---:|
| `comentarios_por_partido` | 1.000.128 | 22,398 s | 44.652 filas/s | 0 |
| `comentarios_por_usuario` | 1.000.128 | 23,782 s | 42.054 filas/s | 0 |

La partición `PAR-0001` y bucket `203006131800` devolvió 1.200 filas. El análisis completo del ambiente, la distribución y las limitaciones se encuentra en `docs/rendimiento.md`.

Los resultados pueden variar según el hardware y el estado del equipo. Deben registrarse los valores reales de cada nueva ejecución.

## 13. Detener y volver a iniciar el ambiente

Detener el contenedor sin eliminar los datos:

```powershell
docker compose stop
```

Volver a iniciarlo:

```powershell
docker compose start
```

Los datos se conservan mediante el montaje local:

```text
~/docker/data/cassandra
```

No se debe eliminar esa carpeta salvo que se busque comenzar explícitamente desde cero.

## 14. Documentación

- `docs/patrones_de_acceso.md`: preguntas prioritarias, entradas, orden, límites y frecuencia.
- `docs/modelo_tabular.md`: keyspace, tablas, columnas, claves y relación con las consultas.
- `docs/decisiones_de_particionamiento.md`: buckets, supuestos, duplicación y riesgos.
- `docs/rendimiento.md`: ambiente, volumen, tasas reales, distribución y limitaciones.
- `docs/evidencia/`: capturas verificables de la ejecución.

## 15. Decisiones y limitaciones principales

- Cassandra se modeló desde las consultas y no como una tabla SQL genérica.
- La clave principal por partido es `(partido_id, bucket_10min)`.
- La tabla secundaria utiliza `(usuario_id, bucket_dia)`.
- `creado_en` ordena los comentarios de forma descendente dentro de cada partición.
- `comentario_id` completa la unicidad de cada fila.
- No se utiliza `ALLOW FILTERING` como solución de diseño.
- No se aplica TTL en esta primera versión para evitar tombstones innecesarios durante las pruebas.
- El nodo único local no demuestra replicación real, tolerancia a fallas ni comportamiento multirregional.
- No se publican credenciales personales ni secretos reales.

## 16. Resultado

El módulo permite crear el ambiente, repetir el esquema y la carga de muestra de forma idempotente, ejecutar CRUD y consultas compatibles con las claves, generar más de un millón de comentarios y medir la carga real sobre las dos tablas de acceso.
