# Hito 6 - Decisiones de particionamiento

## 1. Criterio general

El diseño parte de los patrones de acceso documentados. No se intenta crear una tabla única para responder cualquier pregunta ni trasladar un modelo relacional a Cassandra.

Los comentarios se consultarán principalmente por partido y por tiempo. Como un partido popular puede concentrar una cantidad muy alta de escrituras, usar solamente `partido_id` como clave de partición produciría una partición que crecería durante toda la actividad del encuentro.

## 2. Supuestos de volumen

- El Hito 5 contiene 96 partidos, identificados desde `PAR-0001` hasta `PAR-0096`.
- El mecanismo de carga del Hito 6 deberá superar 1.000.000 de comentarios.
- La plataforma completa fue planteada para millones de usuarios concurrentes y picos globales superiores a 100.000 solicitudes por segundo. Esos valores no representan escrituras medidas en Cassandra.
- Para estimar la distribución se considera una ventana de actividad de aproximadamente 120 minutos por partido.
- La distribución será desigual porque algunos partidos pueden ser más populares que otros.

Con 1.000.000 de comentarios distribuidos entre 96 partidos, el promedio teórico es de aproximadamente 10.417 comentarios por partido. Si cada partido utiliza 12 buckets de diez minutos, el promedio teórico es de aproximadamente 868 comentarios por partición. Este cálculo sirve como referencia de diseño y no como garantía de producción.

## 3. Tabla principal: partición por partido y bucket de diez minutos

La tabla principal utilizará una clave de partición compuesta por:

```text
(partido_id, bucket_10min)
```

El bucket será un texto que representa un intervalo de diez minutos. Por ejemplo:

```text
203006132000
```

Este valor representa el intervalo iniciado el 13 de junio de 2030 a las 20:00. Los comentarios entre las 20:00 y las 20:09:59 compartirán ese bucket; a las 20:10 comenzará otro.

### Justificación

- `partido_id` mantiene juntos los comentarios del contexto deportivo consultado.
- `bucket_10min` impide que la partición crezca durante todo el partido.
- La partición activa cambia cada diez minutos y limita temporalmente la concentración.
- Una consulta de comentarios recientes normalmente accede al bucket actual.
- Una ventana que cruce un límite de bucket se ejecutará sobre cada bucket necesario, sin usar `ALLOW FILTERING`.

El bucket temporal reduce el crecimiento y la duración de la concentración, pero no convierte al laboratorio de un nodo en un sistema de alta disponibilidad. Su resultado deberá analizarse con la medición real.

## 4. Clustering de la tabla principal

Dentro de cada partición, las filas se ordenarán por:

```text
creado_en DESC, comentario_id ASC
```

`creado_en DESC` permite recuperar primero los comentarios más recientes. `comentario_id` completa la identidad de la fila cuando dos comentarios poseen el mismo instante de creación.

## 5. Tabla secundaria: partición por usuario y día

El historial de un usuario no se resolverá filtrando la tabla principal. Se utilizará una tabla adicional con la clave de partición:

```text
(usuario_id, bucket_dia)
```

El bucket diario tendrá el formato `AAAAMMDD`, por ejemplo `20300613`.

### Justificación

- `usuario_id` agrupa los comentarios del autor solicitado.
- `bucket_dia` evita que el historial completo del usuario forme una partición ilimitada.
- La consulta de actividad reciente puede comenzar por el día conocido.
- Los comentarios se ordenarán por `creado_en DESC` y luego por `comentario_id ASC`.

## 6. Duplicación controlada

Cada comentario se almacenará en la tabla principal por partido y también en la tabla secundaria por usuario. Esta duplicación se acepta porque cada tabla responde a una consulta concreta.

El costo es que una actualización o eliminación deberá aplicarse a ambas tablas utilizando sus claves completas. No se utilizarán joins ni filtros globales para reconstruir el historial.

## 7. Expiración y borrado

La primera versión no aplicará TTL automático. Los comentarios permanecerán disponibles para las pruebas y la evidencia. Las eliminaciones serán puntuales y controladas porque `DELETE` y TTL producen tombstones.

## 8. Alcance del laboratorio

El keyspace local utilizará `SimpleStrategy` con factor de replicación 1 porque el entorno tiene un único nodo. Esta configuración permite comprobar CQL y el modelado, pero no demuestra tolerancia a fallas, alta disponibilidad ni distribución multirregional.

