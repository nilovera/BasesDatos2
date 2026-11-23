# Fixture 2030 — Capacidad, SLO, RPO/RTO y plan de validación

**Estado:** propuesta cuantitativa para validación  
**Versión:** 1.0  
**Fecha:** 2 de noviembre de 2026  
**Documentos base:** `02_patrones_acceso_y_requisitos_fixture2030.md`, `04_arquitectura_distribuida_cap_consistencia.md` y `05_diagramas_arquitectura_fixture2030.md`

---

## 1. Propósito

Este documento convierte las decisiones de arquitectura de Fixture 2030 en objetivos verificables. Define:

1. Escenarios de carga.
2. Volúmenes y tasas de operación.
3. Objetivos de latencia, disponibilidad y frescura.
4. RPO y RTO por subsistema.
5. Pruebas de rendimiento, resiliencia y recuperación.
6. Criterios de aprobación y formato de evidencia.

Los valores no representan capacidad productiva ya demostrada. Se clasifican como:

| Clasificación | Significado |
|---|---|
| **Medido** | Resultado obtenido en una ejecución fechada y con evidencia. |
| **Objetivo de laboratorio** | Umbral que deberá cumplir la implementación académica. |
| **Hipótesis de arquitectura** | Carga utilizada para dimensionar semifinales y final; debe validarse con el profesor. |
| **Estimación** | Cálculo derivado de una hipótesis; no reemplaza una prueba. |

Esta distinción es obligatoria para conservar la trazabilidad solicitada por el profesor.

---

## 2. Principios de medición

### 2.1 Promedio no es suficiente

La latencia se informará como mínimo mediante:

- Promedio.
- Mediana.
- `p95`.
- `p99`.
- Máximo.
- Tasa de error.
- Throughput observado.

El `p95` representa el tiempo que no supera el 95 % de las solicitudes. El `p99` permite observar la cola lenta que suele crecer durante saturación, pausas, failover o compaction.

### 2.2 La carga generada también se mide

No alcanza con configurar una cantidad de usuarios virtuales. Cada prueba registrará:

- Usuarios concurrentes efectivos.
- Solicitudes por segundo generadas.
- Operaciones por segundo confirmadas.
- Errores y timeouts.
- CPU, memoria, disco y red del generador.
- CPU, memoria, disco y red del sistema bajo prueba.

Si el generador llega al 100 % de CPU, la prueba no demuestra el límite del backend.

### 2.3 El éxito funcional sigue siendo obligatorio

Un resultado rápido pero incorrecto no aprueba. Durante la carga se controlará que:

- No se dupliquen eventos oficiales.
- El marcador coincida con los goles confirmados.
- No se pierdan comentarios confirmados.
- Las sustituciones respeten la alineación activa.
- Las proyecciones converjan después del atraso.
- Las estadísticas conserven el timestamp original.

### 2.4 Laboratorio y arquitectura objetivo no se mezclan

Una notebook puede validar modelos, scripts, idempotencia y comportamiento relativo. No puede demostrar por sí sola que la arquitectura soporta un millón de espectadores.

La entrega informará por separado:

- Resultado local real.
- Extrapolación o cálculo.
- Arquitectura necesaria para el objetivo.
- Aspectos que requieren infraestructura distribuida real.

### 2.5 Línea base heredada del Hito 10

La evidencia del Hito 10 registró, el 10 de octubre de 2026:

- 60 solicitudes exitosas de 60.
- 10 solicitudes medidas por motor.
- Concurrencia igual a 1.
- Promedio general de 23,57 ms.
- Integración local de seis motores.

Ese resultado se conserva como **baseline histórico de integración**, no como prueba de capacidad. No informa p95/p99 bajo concurrencia ni comportamiento durante saturación. Además, incluía IRIS, motor que fue excluido de la arquitectura objetivo posterior. Las nuevas pruebas deberán ejecutarse sobre la solución actualizada y no mezclar ambas configuraciones.

---

## 3. Modelo de carga de referencia

### 3.1 Niveles

Los siguientes valores son hipótesis de diseño. Permiten construir pruebas proporcionales mientras la cátedra no defina una escala obligatoria.

| Escenario | Espectadores concurrentes | Consulta de estado cada 10 s | Comentarios sostenidos | Ráfaga de comentarios | Estado |
|---|---:|---:|---:|---:|---|
| Partido habitual | 25.000 | 2.500 lecturas/s | 100/s | 500/s | Hipótesis |
| Semifinal | 250.000 | 25.000 lecturas/s | 1.000/s | 5.000/s | Hipótesis |
| Final | 1.000.000 | 100.000 lecturas/s | 2.000/s | 10.000/s durante 30 s | Hipótesis |

La fórmula de lectura con polling es:

```text
lecturas_por_segundo = usuarios_concurrentes / intervalo_de_actualización
```

Un millón de clientes consultando cada diez segundos produce 100.000 solicitudes por segundo. Por eso el estado público debe servirse desde Redis y una capa de API horizontal, no desde MongoDB en cada lectura.

En una evolución productiva se deberá evaluar difusión por `SSE`, WebSocket o caché perimetral. Para el trabajo académico se mantiene REST y se documenta esta limitación.

### 3.2 Ráfaga posterior a un evento

La prueba de final incluirá una ráfaga después de:

- Gol.
- Penal.
- Tarjeta roja.
- Finalización.
- Inicio de una tanda de penales.

La ráfaga de referencia será:

```text
10.000 comentarios/s × 30 s = 300.000 intentos de publicación
```

El sistema puede aplicar rate limiting y rechazar excedentes con una respuesta explícita. No puede aceptar silenciosamente una publicación y después perderla.

### 3.3 Volumen total de comentarios de una final

Para dimensionar almacenamiento se utilizará una media de 1.000 comentarios/s durante 120 minutos:

```text
1.000 × 7.200 segundos = 7.200.000 comentarios
```

Con un tamaño preliminar de 1 KiB por comentario y RF 3:

```text
7.200.000 × 1 KiB × 3 ≈ 20,6 GiB replicados
```

Es una estimación sin compaction, índices, overhead ni compresión. El tamaño real deberá medirse con el esquema definitivo.

### 3.4 Particionado de comentarios en semifinal y final

La clave propuesta es:

```text
((partido_id, bucket_1min, shard), creado_en, comentario_id)
```

Con 10.000 publicaciones/s:

| Shards | Escrituras/s por shard | Comentarios por partición de 1 min | Tamaño preliminar a 1 KiB |
|---:|---:|---:|---:|
| 4 | 2.500 | 150.000 | 146 MiB |
| 8 | 1.250 | 75.000 | 73 MiB |
| 16 | 625 | 37.500 | 37 MiB |

La prueba comparará 4, 8 y 16 shards. La elección no se congelará hasta medir latencia, distribución, tamaño de partición y costo de reconstruir el feed.

### 3.5 Estadísticas de equipo

Se mantiene la definición congruente con el Hito 8:

```text
Intervalo = 10 segundos
Precisión = segundos
Resumen = 15 minutos
```

| Duración | Cálculo | Puntos por partido |
|---|---|---:|
| 90 minutos | 2 equipos × 5.400 s / 10 s | 1.080 |
| 120 minutos | 2 equipos × 7.200 s / 10 s | 1.440 |

### 3.6 Posiciones y mapas de calor

El intervalo posicional es independiente de las estadísticas de equipo.

| Frecuencia | 90 minutos, 22 jugadores activos | 120 minutos, 22 jugadores activos | Uso |
|---:|---:|---:|---|
| 1 Hz | 118.800 puntos | 158.400 puntos | Objetivo académico propuesto |
| 5 Hz | 594.000 puntos | 792.000 puntos | Hipótesis productiva de mayor detalle |

La implementación académica comenzará con 1 Hz. Las sustituciones no aumentan la cantidad de jugadores simultáneos: cambian la identidad de la serie activa.

---

## 4. SLI y SLO

### 4.1 Definiciones

| Concepto | Aplicación en Fixture 2030 |
|---|---|
| **SLI** | Métrica observada: latencia, errores, frescura, lag o disponibilidad. |
| **SLO** | Umbral interno que el sistema busca cumplir. |
| **SLA** | Compromiso contractual. No se definirá uno para el trabajo académico. |

### 4.2 Objetivos de latencia y error

Los siguientes son objetivos de arquitectura. En laboratorio se registrará el resultado real y se indicará si cumple o no.

| Operación | Fuente principal | p95 | p99 | Errores bajo carga objetivo |
|---|---|---:|---:|---:|
| Consultar estado y marcador caliente | Redis | ≤ 100 ms | ≤ 250 ms | < 0,1 % |
| Registrar evento oficial | MongoDB majority | ≤ 250 ms | ≤ 750 ms | < 0,1 % sin contar rechazos válidos |
| Consultar fixture o catálogo | Redis/MongoDB | ≤ 200 ms | ≤ 500 ms | < 0,5 % |
| Publicar comentario | Cassandra `LOCAL_QUORUM` | ≤ 300 ms | ≤ 900 ms | < 1 % |
| Leer comentarios recientes | Redis/Cassandra `LOCAL_ONE` | ≤ 200 ms | ≤ 500 ms | < 0,5 % |
| Validar sesión | Redis | ≤ 50 ms | ≤ 150 ms | < 0,1 % |
| Consultar última estadística | Redis/InfluxDB | ≤ 200 ms | ≤ 600 ms | < 0,5 % |
| Consultar histórico 15 m | InfluxDB | ≤ 1 s | ≤ 3 s | < 1 % |
| Generar mapa de calor acotado | InfluxDB/agregado | ≤ 1,5 s | ≤ 4 s | < 1 % |
| Consultar navegación de grafo | Neo4j opcional | ≤ 500 ms | ≤ 2 s | < 1 % |

Los códigos `409`, `422`, `429` y `503` esperados por reglas, rate limit o degradación no se mezclarán con errores inesperados. Se medirán por separado.

### 4.3 Objetivos de frescura

| Dato visible | Retraso p95 permitido | Respuesta si se supera |
|---|---:|---|
| Marcador y estado público | 2 s | Mostrar `actualizado_en`; alertar y consultar fuente oficial con límite. |
| Evento en timeline caliente | 3 s | Marcar timeline atrasado y conservar orden por secuencia. |
| Estadística reciente | 5 s | Estado `atrasado` o `parcial`. |
| Ranking en vivo | 15 s | Mostrar `calculado_en` y versión. |
| Auditoría consultable | 30 s | Mantener evidencia en `outbox`; alertar por lag. |
| Neo4j | 60 s | Deshabilitar navegación compleja o usar respuesta reducida. |

### 4.4 Objetivos de disponibilidad

| Capacidad | SLO mensual objetivo | Presupuesto aproximado de indisponibilidad en 30 días |
|---|---:|---:|
| Lectura del partido y marcador | 99,95 % | 21,6 min |
| Escritura oficial | 99,9 % | 43,2 min |
| Comentarios | 99,5 % | 216 min |
| Estadísticas recientes | 99,5 % | 216 min |
| Neo4j y multimedia no crítica | 99,0 % | 432 min |

Durante una final se evaluará además una ventana crítica de 150 minutos. La degradación social no deberá provocar indisponibilidad del núcleo oficial.

---

## 5. RPO y RTO

### 5.1 Definiciones

- **RPO:** cantidad máxima de datos que se acepta perder, medida hacia atrás desde el incidente.
- **RTO:** tiempo máximo objetivo para recuperar la capacidad definida.

Un RPO de cero solo se declara dentro del dominio donde existe replicación síncrona o quórum. No implica automáticamente RPO cero frente a la pérdida de una región completa.

### 5.2 Fallo de nodo dentro de la región principal

| Subsistema | RPO objetivo | RTO objetivo | Condición de aprobación |
|---|---:|---:|---|
| MongoDB oficial | 0 para operaciones confirmadas por mayoría | ≤ 60 s | Nuevo primary; sin gol duplicado ni perdido. |
| Cassandra comentarios | 0 para publicaciones confirmadas por quórum | Sin interrupción funcional; reparación posterior | Publica con dos réplicas y mantiene orden. |
| Redis caché | No aplica | ≤ 5 min | Reconstrucción desde fuentes durables. |
| Redis sesiones | ≤ 1 s con AOF y réplica | ≤ 2 min | Sesiones recuperadas o reautenticación controlada. |
| InfluxDB | ≤ intervalo del buffer durable | ≤ 15 min | Reproducción preservando timestamps. |
| Neo4j | 0 lógico, porque es reconstruible | ≤ 30 min | Checkpoint alcanza la secuencia oficial. |
| Auditoría | 0 en `outbox` | ≤ 30 min para consulta | Todos los registros pendientes son proyectados. |

### 5.3 Pérdida completa de la región principal

La arquitectura propuesta no mantiene dos regiones activas para escrituras oficiales. La promoción será controlada.

| Dominio | RPO regional preliminar | RTO regional preliminar | Dependencia |
|---|---:|---:|---|
| Datos oficiales MongoDB | ≤ 5 min | ≤ 15 min | Réplica diferida, oplog o backup remoto validado. |
| Comentarios Cassandra | ≤ 5 min | ≤ 15 min | Estrategia multidatacenter o backup incremental. |
| Estadísticas | ≤ 10 s | ≤ 30 min | Buffer durable externo y lotes reproducibles. |
| Sesiones | Se admite pérdida y reautenticación | ≤ 15 min | Nuevo Redis y restauración mínima. |
| Cachés y rankings | No aplica | ≤ 15 min | Reconstrucción. |
| Neo4j | No aplica | ≤ 2 h | Reconstrucción completa o incremental. |
| Multimedia y archivos | Según última réplica confirmada | ≤ 60 min | Replicación y versionado del object storage. |

Estos tiempos solo serán compromisos finales después de una prueba de restauración. Generar un backup sin restaurarlo no demuestra recuperación.

---

## 6. Plan de pruebas

### 6.1 Herramientas propuestas

| Herramienta | Responsabilidad |
|---|---|
| Pytest | Contratos, reglas, idempotencia e integración. |
| Postman y ejecución automatizada | Colección demostrable y regresión del contrato REST. |
| Locust con Python | Carga, concurrencia, ramp-up, ráfagas y ejecución distribuida. |
| Scripts Docker/PowerShell | Detención, reinicio y recuperación de nodos. |
| Métricas del sistema y motores | CPU, RAM, disco, red, conexiones, colas y lag. |

Postman no reemplazará la herramienta de carga. Se utilizará para demostrar el contrato funcional. Locust permite modelar usuarios en Python y distribuir generación entre procesos o máquinas cuando un solo generador no alcanza.

### 6.2 Matriz de pruebas

| ID | Prueba | Carga | Falla | Resultado esperado |
|---|---|---|---|---|
| P01 | Regresión funcional | 1 usuario | Ninguna | Reglas y códigos correctos. |
| P02 | Baseline | 1 usuario, 30 repeticiones por operación | Ninguna | Latencia base sin concurrencia. |
| P03 | Carga académica | Escala soportada por la notebook durante 15 min | Ninguna | p95/p99 estables y sin errores funcionales. |
| P04 | Semifinal relativa | `5x` respecto de P03 | Ninguna | Degradación controlada; sin afectar núcleo oficial. |
| P05 | Final relativa | `10x` respecto de P03 durante 30 min | Ninguna | Cumplir umbral definido o identificar saturación. |
| P06 | Ráfaga de gol | `20x` durante 30 s | Ninguna | Backpressure y `429`; sin pérdida silenciosa. |
| P07 | Soak del partido | Carga estable durante 120 min | Ninguna | Sin fuga de memoria ni crecimiento ilimitado de lag. |
| P08 | Final con Cassandra degradada | `10x` | Un nodo detenido | Quórum disponible y capacidad reducida. |
| P09 | Partición Cassandra `2 + 1` | Publicaciones y lecturas | Red dividida | Solo lado con quórum confirma. |
| P10 | Failover MongoDB | Eventos oficiales repetidos | Primary detenido | Nuevo primary, idempotencia y marcador correcto. |
| P11 | Redis caído | Lecturas y sesiones | Redis detenido | Núcleo preservado, caché reconstruible, reautenticación. |
| P12 | InfluxDB caído | Ingesta posicional | InfluxDB detenido | Lotes durables y replay ordenado. |
| P13 | Worker atrasado | Eventos oficiales | Worker detenido | `outbox` crece y luego converge sin duplicados. |
| P14 | Restauración regional simulada | Dataset completo | Región primaria no disponible | Cumplir RPO/RTO preliminar o documentar brecha. |
| P15 | Shards de comentarios | 4, 8 y 16 | Ninguna | Elegir cantidad mediante latencia y tamaño de partición. |

### 6.3 Escalera de carga local

La notebook no intentará simular directamente el escenario arquitectónico de un millón de usuarios. Se buscará el punto de saturación local:

1. Calentamiento de cinco minutos.
2. Incrementos de usuarios en pasos constantes.
3. Cinco minutos por escalón.
4. Detención cuando `p99`, errores o recursos superen los límites.
5. Repetición del último escalón estable.
6. Repetición con una dependencia degradada.

El resultado será:

```text
capacidad_local_estable = mayor throughput repetible que cumple criterios
```

No se multiplicará linealmente esa cifra para prometer capacidad productiva. Servirá para comparar configuraciones y encontrar cuellos de botella.

---

## 7. Criterios de aprobación

### 7.1 Núcleo oficial

Una prueba aprueba solo si:

- Cero eventos oficiales confirmados se pierden.
- Cero eventos se duplican ante reintentos.
- El marcador final coincide con eventos válidos.
- Una operación sin mayoría se rechaza.
- El failover no habilita dos escritores.
- El `outbox` converge después de recuperar workers.

### 7.2 Comentarios

- Toda respuesta `201` corresponde a un comentario recuperable.
- La minoría sin quórum no confirma publicaciones.
- El feed puede atrasarse, pero no rompe su cursor ni su orden local.
- Los rechazos por límite se informan como `429`.
- La pérdida de Redis no elimina comentarios confirmados.
- La opción de shards elegida mantiene tamaño y latencia dentro de los objetivos.

### 7.3 Estadísticas y mapas de calor

- Los lotes reintentados no duplican puntos.
- Los timestamps originales se conservan.
- Los puntos fuera del intervalo en cancha se rechazan o excluyen.
- El mapa del saliente termina y el del suplente comienza en la sustitución.
- La respuesta informa frescura y granularidad.

### 7.4 Rendimiento

- Tasa de error inesperado dentro del SLO.
- p95 y p99 dentro del objetivo o brecha documentada.
- Sin saturación del generador de carga.
- Sin crecimiento continuo de memoria o colas después de estabilizar la carga.
- Recuperación dentro de RTO y pérdida dentro de RPO.

Una prueba que no cumple sigue siendo evidencia útil si se conserva el resultado, se identifica el cuello de botella y no se presenta como aprobada.

---

## 8. Métricas obligatorias

### API

- RPS por endpoint y código HTTP.
- p50, p95, p99 y máximo.
- Requests activas.
- Timeouts.
- Pool de conexiones.
- Circuit breaker por dependencia.

### MongoDB

- Latencia de escritura majority.
- Replication lag.
- Elecciones.
- Operaciones por segundo.
- Conexiones y colas.

### Cassandra

- Latencia de lectura y escritura.
- Throughput por nodo.
- Particiones calientes.
- Compactions pendientes.
- Dropped mutations.
- Tamaño por partición.
- Estado y reparación de nodos.

### Redis

- Hits, misses y hit ratio.
- Memoria utilizada.
- Evictions.
- Expired keys.
- Replication lag.
- Operaciones por segundo.

### InfluxDB

- Puntos aceptados y rechazados.
- Latencia de ingesta y consulta.
- Lag del buffer.
- Tamaño de lotes.
- Compresión y almacenamiento.

### Proyecciones

- Secuencia oficial actual.
- Checkpoint del consumidor.
- Cantidad de mensajes pendientes.
- Edad del mensaje más antiguo.
- Duplicados descartados.

---

## 9. Trazabilidad de evidencias

Cada ejecución tendrá un identificador estable:

```text
EVID-AAAA-MM-DD-TIPO-NN
```

Ejemplo:

```text
EVID-2026-11-15-CARGA-03
```

### 9.1 Registro mínimo

| Campo | Contenido obligatorio |
|---|---|
| ID | Identificador de evidencia. |
| Fecha y zona horaria | Inicio y fin. |
| Responsable | Integrante que ejecutó. |
| Commit | Hash exacto del código. |
| Infraestructura | CPU, RAM, SO, Docker y topología. |
| Configuración | Nodos, réplicas, niveles de consistencia y límites. |
| Dataset | Cantidad y tamaño. |
| Script | Ruta y parámetros exactos. |
| Esperado | Umbral o comportamiento. |
| Observado | Métricas y salida. |
| Resultado | Aprobado, rechazado o inconcluso. |
| Archivos | TXT/CSV/JSON/XML y capturas vinculadas. |
| Conclusión | Qué decisión confirma o contradice. |

### 9.2 Matriz requisito–prueba–evidencia

| Requisito | Prueba | Evidencia futura |
|---|---|---|
| Un gol confirmado no se pierde | P10 | Log de comandos, marcador antes/después y tiempo de elección. |
| Comentarios toleran un nodo caído | P08 | Métricas por nodo y publicaciones recuperadas. |
| Minoría Cassandra no confirma | P09 | Respuestas de ambos lados de la partición. |
| Redis es reconstruible | P11 | Conteos antes, vaciado, reconstrucción y comparación. |
| InfluxDB acepta replay idempotente | P12 | Lote original, replay y conteo final sin duplicados. |
| Proyecciones convergen | P13 | Secuencia oficial y checkpoint antes/después. |
| RPO/RTO regional | P14 | Timeline del incidente y diferencias de datos. |
| Sharding evita hotspot | P15 | Comparación 4/8/16 con p95, p99 y tamaño. |

---

## 10. Decisiones fijadas en este paso

1. Los resultados se informan con p95 y p99, no solo promedio.
2. El escenario de final se modela por separado y contiene ráfagas.
3. La publicación social puede limitarse antes que afectar el núcleo oficial.
4. La prueba local determina capacidad local, no capacidad productiva.
5. Postman conserva el rol de prueba funcional; la carga se modela en Python.
6. Los RPO/RTO se definen por dominio y por tipo de falla.
7. RPO cero local no implica RPO cero regional.
8. Cada requisito debe vincularse con una ejecución fechada y reproducible.
9. La cantidad de shards se decide mediante comparación, no por intuición.
10. La frecuencia académica propuesta para posiciones es 1 Hz.

---

## 11. Decisiones pendientes

1. Validación docente de los escenarios de 25.000, 250.000 y 1.000.000 espectadores.
2. Confirmación de la frecuencia posicional de 1 Hz.
3. Recursos máximos permitidos para la prueba académica.
4. Alcance requerido de clústeres multinodo reales.
5. Elección final entre 4, 8 y 16 shards.
6. Mecanismo durable de buffer para InfluxDB.
7. Estrategia regional concreta de MongoDB y Cassandra.
8. Umbrales definitivos de latencia exigidos por la cátedra.
9. Herramienta de observabilidad que se implementará.
10. Permanencia o eliminación de Neo4j en la solución final.

---

## 12. Preguntas para el profesor

### Pregunta 1 — Escala

¿Podemos utilizar 25.000 espectadores para un partido habitual, 250.000 para una semifinal y 1.000.000 para la final como hipótesis de dimensionamiento, aclarando que la prueba local será proporcional?

### Pregunta 2 — Capacidad demostrable

¿Se espera una prueba multinodo con una tasa mínima o alcanza con medir el límite local, ejecutar escalas relativas `1x`, `5x` y `10x`, e indicar qué topología soportaría el objetivo arquitectónico?

### Pregunta 3 — Fallos

¿La entrega debe demostrar particiones de red y failover reales o puede combinar caída de contenedores, simulación documentada y recuperación verificada?

### Pregunta 4 — RPO/RTO

¿La cátedra exige valores determinados o podemos proponerlos según criticidad y validarlos con pruebas de restauración?

### Pregunta 5 — Datos posicionales

¿Es aceptable una frecuencia académica de 1 Hz para mapas de calor, manteniendo 10 segundos solamente para estadísticas de equipo?

---

## 13. Referencias utilizadas

- Clase 1: volumen, velocidad, latencia y escalabilidad horizontal.
- Clase 3: CAP, replicación, particionamiento, N/R/W y comportamiento ante fallos.
- Clase 4: índices, replica sets, sharding y medición de rendimiento.
- Clase 6: modelado por consultas, particiones, clustering y consistencia ajustable de Cassandra.
- Clase 8: caché, TTL, AOF, evicción y Redis Cluster.
- [Documentación oficial de Locust — ejecución distribuida](https://docs.locust.io/en/stable/running-distributed.html).
- [Documentación oficial de Postman — referencia de ejecución de colecciones](https://learning.postman.com/docs/reference/overview).

---

## 14. Historial de cambios

### Versión 1.0 — 2 de noviembre de 2026

- Modelo cuantitativo para partido habitual, semifinal y final.
- Estimación de comentarios, estadísticas y mapas de calor.
- SLI/SLO de latencia, error, frescura y disponibilidad.
- RPO/RTO local y regional.
- Matriz de quince pruebas.
- Criterios de aceptación por dominio.
- Formato obligatorio de trazabilidad.
- Preguntas para validación docente.

