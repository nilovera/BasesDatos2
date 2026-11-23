# Fixture 2030 — Plan maestro del trabajo final

**Versión:** 1.0  
**Fecha:** 2 de noviembre de 2026  
**Estado:** hoja de ruta de trabajo; requisitos académicos pendientes de cotejo final.  
**Regla:** los números de paso de este documento permanecen fijos.

## 1. Diagnóstico: ¿vamos por buen camino?

Sí, el recorrido de diseño está alineado con la materia: necesidad de negocio → patrón de acceso → comparación de modelos → arquitectura distribuida → modelo físico → integración → implementación → evidencia.

Sin embargo, todavía no corresponde afirmar que el trabajo final cumple el 100 % de los requisitos. Hay documentos de diseño, implementaciones históricas y extensiones pendientes. Tener un documento no demuestra que su arquitectura funcione ni que el profesor haya aprobado sus supuestos.

El principal valor de la entrega será explicar y demostrar **CAP, consistencia, particionado, replicación, recuperación y escalabilidad**, no solamente conectar bases mediante una API.

### 1.1 Hallazgos que deben resolverse

| Hallazgo | Evidencia disponible | Acción necesaria |
|---|---|---|
| Volúmenes diferentes entre clases e hitos | Clase 1: 64 equipos, 127 partidos y más de 1.500 jugadores. Clase 4: 64 equipos y más de 1.000 jugadores. Laboratorio reportado: 1.024 jugadores y 96 partidos en Neo4j. | Confirmar volumen exigido en la consigna final; distinguir dataset del hito de dataset final. No presentar 96 como fixture completo sin justificación. |
| Alcance de motores cerrado | El recorrido de la materia contempló MongoDB, Neo4j, Cassandra, Redis, IRIS e InfluxDB. La arquitectura ejecutable final utiliza cinco motores y excluye IRIS. | Conservar la comparación como evidencia y aplicar ADR-001: responsabilidades reasignadas, API y Docker sin dependencias de IRIS. |
| Neo4j opcional en el diseño objetivo | El Hito 5 exige modelo y consultas de grafo; los documentos recientes condicionan su permanencia a consultas útiles. | Evaluar valor técnico y obligatoriedad académica antes de decidir. |
| Escala objetivo no demostrada | El anexo propone audiencias y tasas para semifinal/final. | Mantenerlas como hipótesis; medir capacidad local por separado. |
| Falta cotejo integral de consignas posteriores | Se dispone de clases, devoluciones y resultados reportados, pero no de todas las consignas originales ni de la rúbrica final completa en este conjunto. | Incorporarlas a la matriz de requisitos. No inventar requisitos de hitos faltantes. |

## 2. Fuentes y orden de autoridad

1. Consigna final y aclaraciones escritas del profesor.
2. Consigna y rúbrica específica de cada hito.
3. Devoluciones del profesor.
4. Material teórico de las clases.
5. Decisiones y documentos de arquitectura del grupo.
6. Código y evidencia ejecutada: determinan qué está realmente implementado, no qué sería deseable.

Cuando dos fuentes difieran, se registra el conflicto y se solicita una definición. La numeración de una clase no se equipara automáticamente a la de un hito: por ejemplo, Redis aparece en Clase 8, pero la entrega reportada fue Hito 7.

## 3. Documentos existentes y ubicación dentro del plan

| Documento | Paso al que pertenece | Estado real |
|---|---|---|
| `alcance_funcional_fixture2030.md` | 1 | Base funcional acordada; conserva consultas para el profesor. |
| `02_patrones_acceso_y_requisitos_fixture2030.md` | 2 | Análisis realizado; faltan parámetros definitivos. |
| `03_comparacion_motores_y_estrategia_cap.md` | 3 | Comparación y responsabilidades; decisiones condicionadas explícitas. |
| `04_arquitectura_distribuida_cap_consistencia.md` | 4 | Arquitectura objetivo diseñada; no equivale a clúster desplegado. |
| `05_diagramas_arquitectura_fixture2030.md` | 5 | Tres vistas elaboradas; requieren revisión técnica y renderizado final. |
| `05B_objetivos_capacidad_slo_rpo_rto_y_pruebas.md` | Anexo del paso 5 | Objetivos e hipótesis cuantitativas, no resultados productivos. |
| `00_plan_maestro_fixture2030.md` | Transversal | Referencia única para orden y estado del trabajo. |

El anexo 05B se llamaba `06_objetivos_capacidad_slo_rpo_rto_y_pruebas.md`. Fue renombrado para liberar el número 6. El cambio de nombre no altera sus resultados ni convierte sus hipótesis en compromisos aprobados.

Los apartados antiguos titulados «próxima etapa» reflejan el momento en que se escribió cada documento. El orden vigente es el de este plan maestro.

## 4. Plan de pasos fijos

| Paso | Trabajo | Relación con los hitos | Entregable y condición de cierre | Situación |
|---:|---|---|---|---|
| 1 | Contexto, actores, alcance y reglas funcionales | Hito 1: diagnóstico | Inventario completo, dentro/fuera de alcance y preguntas abiertas. | Documento elaborado. |
| 2 | Patrones de acceso y requisitos | Hitos 1–2 | Lecturas, escrituras, claves de acceso, volumen, latencia, consistencia, retención y fallos por necesidad. | Documento elaborado; cifras pendientes. |
| 3 | Comparar modelos y asignar responsabilidades | Hito 2 | Comparación de los seis modelos; alternativas, trade-offs y una fuente autoritativa por dato. | Documento elaborado; validación académica pendiente. |
| 4 | Arquitectura distribuida | Hito 3 | CAP por operación, replicación, particionado, recuperación y escenarios semifinal/final. | Diseño elaborado, no demostrado. |
| 5 | Diagramas y viabilidad cuantitativa | Hito 3 y devoluciones H7–H8 | Réplicas, zonas, quórum y fallos visibles; anexo 05B con objetivos y pruebas. | Documentos elaborados; revisión de coherencia pendiente. |
| 6 | Diseño físico por base | Hitos de MongoDB, Neo4j, Cassandra, Redis e InfluxDB | Esquemas, claves, índices, validación, TTL, consultas y reconstrucción; cada estructura tiene una consulta que la justifica. | Próximo trabajo de diseño. |
| 7 | Contratos internos y sincronización | Integración API del Hito 10 y arquitectura H3 | Eventos, productores, consumidores, idempotencia, orden, reintentos, auditoría y reconciliación. | Pendiente. |
| 8 | Brecha y reutilización de hitos | Todos los hitos existentes | Inventario de repositorios, código, datos y pruebas; plan de migración con costos y dependencias. | Pendiente de inspección del código actual. |
| 9 | Implementación incremental | Hitos técnicos e integración | Flujos completos funcionando y verificaciones por incremento, sin rehacer módulos válidos. | Componentes históricos disponibles; integración final pendiente. |
| 10 | Pruebas, congruencia y entrega final | Hitos y rúbrica final | Evidencia fechada y reproducible; matriz requisito–prueba–resultado; documentación y demostración consistentes. | Pruebas históricas disponibles; validación final pendiente. |

**No se agrega un nuevo paso porque aparezca un documento auxiliar.** Se crea un anexo o una subtarea, conservando esta numeración.

## 5. Qué heredamos de cada hito

| Hito | Aprendizaje o componente reutilizable | Devolución o control que llevamos al final |
|---|---|---|
| 1 — Diagnóstico | Inventario de necesidades y contexto de escala. | Justificar por patrón dominante, no solo volumen; explicar duplicación, consistencia y complejidad. |
| 2 — Matriz | Comparación tecnológica y mapa de persistencia. | Comparar los seis modelos por necesidad; no forzar puntuaciones; justificar cambios respecto de la decisión original. |
| 3 — Distribución | CAP, consistencia, réplicas, quórum, particionado y resiliencia. | El diagrama debe permitir reconstruir nodos, mayorías y comportamiento ante fallos. Es un criterio transversal de todo el final. |
| 4 — MongoDB | Catálogo de 64 equipos y 1.024 jugadores reportados, validadores e índices. | Revisar volumen final e integridad; ampliar al núcleo oficial sin invalidar el catálogo existente. |
| 5 — Neo4j | Grafo, restricciones, relaciones y consultas. | Segunda ejecución idempotente; credenciales por entorno; consultas que demuestren valor real. |
| 6 — Cassandra | Comentarios por partido y usuario con buckets. | Evaluar hotspot de final, shards, paginación distribuida y convergencia de tablas. Un nodo RF1 no demuestra RF3. |
| 7 — Redis | Sesiones TTL, caché, AOF, contadores y ranking. | Fecha, entorno, método y enlace directo de cada resultado a evidencia; persistencia no cambia el rol de caché. |
| 8 — InfluxDB | 1.080 puntos detallados y 12 resúmenes reportados. | Conservar 10 s, precisión s y agregación 15 min en scripts y documentación; agregar posiciones con frecuencia independiente. |
| 9 — IRIS, antecedente reportado | Reglas y datos de partidos, eventos y árbitros utilizados después por la API. | No incorporar el motor. Migrar únicamente datos o reglas válidas a MongoDB y eliminar las dependencias ejecutables según ADR-001. |
| 10 — API | FastAPI, OpenAPI, Postman/Newman y 21 pruebas de integración reportadas. | Reejecutar sobre arquitectura nueva; sumar escrituras y sincronización. La versión anterior incluía IRIS y no demuestra el núcleo oficial nuevo. |
| Otros hitos o entrega final | Requisitos aún no cotejados en este conjunto documental. | Incorporar sus consignas antes de afirmar cobertura total. |

La evidencia histórica se conserva con su configuración original. No se cambia retrospectivamente para aparentar que probó la arquitectura nueva.

## 6. Cómo ejecutaremos los pasos restantes

### Paso 6 — Diseño físico por motor

Se hará por subpasos y se revisará antes de pasar al siguiente:

- **6.1 Convenciones comunes:** identificadores, UTC, códigos de equipo/jugador/partido, secuencias, versiones y vocabulario de estados. Resolver que `ARG/MEX` en estadísticas no son automáticamente equivalentes a cualquier `EQ-xx`, y que un mismo partido no puede tener rivales diferentes entre motores.
- **6.2 MongoDB:** equipos, jugadores, usuarios, partidos, alineaciones, participaciones, eventos oficiales, outbox y metadatos multimedia; sedes y árbitros con representación explícita, embebida o referenciada según las consultas. Ejemplos, validadores, índices y límites transaccionales.
- **6.3 Cassandra:** comentarios por partido y usuario; auditoría por servicio y recurso. Buckets, shards, TTL, consistencia y réplica. Histórico de eventos solo si se justifica.
- **6.4 Redis:** claves, estructuras, TTL, control de memoria, reconstrucción y separación entre sesiones temporales autoritativas y caché descartable.
- **6.5 InfluxDB:** estadísticas de equipos/jugadores, posiciones y agregados; identidad del punto, tags/fields, frecuencia, retención y tratamiento de correcciones.
- **6.6 Neo4j:** confirmar exigencia académica y consultas de varios saltos antes de decidir cuánto mantener.
- **6.7 Revisión cruzada:** todas las consultas del paso 2 tienen un camino de acceso; ningún dato tiene dos fuentes oficiales contradictorias.

**Salida prevista:** `06_diseno_fisico_por_base.md`. No se generará todavía código productivo ni se modificarán las bases existentes.

### Paso 7 — Contratos y sincronización

Definir contratos para inicio/finalización de partido, alineación, gol, corrección, sustitución, comentario y recepción de estadísticas. Incluir productor, consumidor, esquema, versión, identificador idempotente y tratamiento de fallos.

No todos los eventos tendrán una secuencia por partido: un comentario, un cambio de perfil y un punto estadístico requieren claves y orden propios. Diferenciar tiempo deportivo, timestamp de origen y momento de recepción.

Cerrar específicamente:

- Atomicidad del cambio oficial y su outbox.
- Fallo entre escribir una proyección y guardar el checkpoint.
- Convergencia de comentarios por partido/usuario.
- Auditoría de operaciones sociales y rechazadas, no solo transacciones oficiales MongoDB.
- Buffer durable de estadísticas y política cuando se llena.
- Correcciones que deben recalcular marcador, rankings y mapas.

**Cierre:** cada escritura durable tiene un resultado definido ante éxito, timeout, duplicado y caída parcial. No es obligatorio incorporar un broker adicional si el mecanismo elegido es suficiente y comprobable.

### Paso 8 — Brecha con código y datos reales

Inspeccionar una versión concreta del trabajo del equipo. Para cada requisito registrar: existe, requiere ajuste, falta, está diseñado solamente o queda fuera de alcance.

Priorizar eliminación de dependencias ejecutables de IRIS, migración selectiva de datos válidos a MongoDB, unificación de IDs y partidos, esquemas de comentarios, outbox, auditoría y mapas. Preservar repositorios y evidencias originales; trabajar con migraciones verificables y respaldo.

La inspección completa se realiza aquí, pero si durante el diseño falta un dato crítico del esquema actual se verifica antes: el plan no obliga a diseñar a ciegas.

**Cierre:** backlog ordenado, dependencias, responsable y prueba de aceptación por tarea. No asignar tareas a nombres inventados.

### Paso 9 — Implementación en incrementos

| Incremento | Flujo completo esperado | Prueba inmediata |
|---|---|---|
| 9.1 Núcleo oficial | Proveedor simulado → API → MongoDB → respuesta confirmada. | Inicio, gol duplicado, corrección y sustitución concurrente. |
| 9.2 Sincronización | Transacción → outbox → Redis/auditoría y proyecciones seleccionadas. | Detener consumidor y comprobar convergencia. |
| 9.3 Interacción | Perfil/sesión → publicación → timeline por partido/usuario. | TTL, límites, moderación y recuperación de tablas. |
| 9.4 Estadística individual | Posiciones → participación → mapa de calor y rankings. | Titular sale, suplente entra; puntos fuera de cancha excluidos. |
| 9.5 Consolidación | API sin dependencia activa de IRIS; contratos y datos unificados. | Regresión OpenAPI/Postman y restauración básica. |

Las pruebas se escriben y ejecutan durante cada incremento. El paso 10 concentra aceptación y evidencia final; no es la primera vez que se prueba el sistema.

### Paso 10 — Aceptación y defensa

Validar funcionalidad, idempotencia, carga, ráfagas, fallos, restauración y congruencia documental. Cada prueba se clasifica como ejecutada, simulada, diseñada o no realizada.

El plan 05B define el catálogo de pruebas, pero la carga de referencia se fijará como una tasa concreta y segura antes de ejecutar `1x/5x/10x`. No se define `1x` como el máximo local para después exigir diez veces ese máximo como capacidad garantizada.

Preparar una demostración reproducible: consultar fixture, iniciar partido, registrar gol, repetirlo sin duplicación, hacer sustitución, ver mapa del suplente, comentar, detener una dependencia, recuperar y mostrar auditoría. Reportar límites encontrados.

## 7. Decisiones estables y pendientes

### Estables dentro del proyecto

- Backend y API en Python; Postman para demostración y regresión funcional.
- Proveedor deportivo simulado; administrador para excepciones, sin operador manual continuo ni rol separado de moderador.
- Sin frontend completo, streaming ni sensores reales.
- MongoDB como fuente oficial propuesta del catálogo y núcleo deportivo.
- Cassandra para comentarios y auditoría consultable; Redis para sesiones y copias calientes; InfluxDB para series temporales.
- Sin IRIS en la arquitectura ejecutable; decisión registrada y controlada mediante ADR-001.
- Auditoría, sustituciones, mapas de calor y rankings incluidos mediante una prueba acotada.
- Estadísticas de equipo cada 10 s y resúmenes de 15 min.

### No congeladas como garantías

- Obligatoriedad de motores en el final y permanencia de Neo4j.
- Volumen final del dataset.
- Audiencia de un millón y ráfaga de 10.000 comentarios/s: hipótesis, no capacidad demostrada.
- Cantidad final de shards, retenciones y frecuencia posicional de 1 Hz: propuestas a validar.
- Topología desplegable con el hardware disponible, tecnología del buffer y transporte del outbox.
- RPO/RTO y SLO, especialmente regionales: objetivos sujetos a configuración y pruebas. AOF más réplica no basta por sí solo para garantizar pérdida máxima de un segundo en cualquier falla.

## 8. Puertas de control

| Puerta | Antes de | Condición |
|---|---|---|
| G0 — Alineación académica | Congelar alcance final | Incorporar consigna/rúbrica final y resolver volúmenes y motores exigidos. El diseño puede avanzar con supuestos señalados. |
| G1 — Diseño coherente | Implementación amplia | Pasos 6–7 revisados; consultas cubiertas y recuperación definida. |
| G2 — Migración segura | Reemplazar datos o componentes | Paso 8 inspeccionado; respaldo, IDs y reglas de migración verificados. |
| G3 — Flujo integrado | Carga y fallos intensivos | Pruebas funcionales e idempotencia aprobadas. |
| G4 — Entrega | Publicar versión final | Matriz completa; evidencia sin secretos; README, scripts y resultados coinciden. |

## 9. Reglas de seguimiento

1. Cada tarea tiene requisito, responsable, entregable, prueba y estado.
2. Estados: pendiente, en diseño, diseñado, implementado, probado, aceptado o bloqueado.
3. «Diseñado» no se reemplaza por «completado» si falta ejecución.
4. Una devolución del profesor se transforma en criterio verificable.
5. Una decisión nueva registra motivo, alternativa descartada, trade-off e impacto en documentos/código.
6. Cambiar un umbral después de fallar una prueba exige justificación y conserva el resultado anterior.
7. No se rehacen hitos válidos: se documenta su evolución y se reejecuta lo afectado.
8. Si una consigna obliga a cambiar el alcance, se versiona el plan; sus números no se desplazan.

## 10. Próximo trabajo concreto

**Paso 6.1: convenciones de datos e identidad; luego 6.2: modelo físico MongoDB.**

En paralelo al diseño, obtener la consigna/rúbrica final y las consignas de hitos posteriores que falten. Son necesarias para asegurar cumplimiento académico, pero no impiden avanzar en IDs, reglas e índices ya justificados.

Este documento fija el plan. No inicia la implementación, no afirma aprobación docente y no modifica las entregas históricas.

