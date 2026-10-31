# Guion de la defensa · 20 minutos (RF13, RNF12)

Grupo 10 · Luciano Corgnali, Nicolás Lovera, Valentino Sabignoso

**Reparto propuesto** (ajustar según quién desarrolló cada hito; **todos** deben poder responder sobre cualquier módulo):

- **A · Nicolás:** MongoDB, Neo4j, Cassandra
- **B · Valentino:** Redis, InfluxDB, IRIS
- **C · Luciano:** API, conectividad, carga y monitoreo (Hitos 11-13)

Recursos: [`presentacion.html`](presentacion.html) (pantalla 1), Grafana/Prometheus/PowerShell (pantalla 2), [`demo.md`](demo.md) con los comandos.

| # | Momento | Min | Quién | Diapositiva / pantalla | Mensaje clave (no leer: decirlo) |
|---|---|---:|---|---|---|
| 1 | **Inicio** | 0:00-2:00 | C | 1-2 | El problema de la FIFA: un Mundial en 6 países y 3 continentes, con datos de naturaleza muy distinta. Nuestra decisión: **una base por patrón de acceso + una API que integra + monitoreo que lo demuestra** |
| 2 | **Arquitectura** | 2:00-5:00 | C | 3 | Recorrido Cliente → API → 6 adaptadores → 6 bases. Qué dato vive en cada una (una sola fuente de verdad por dato). Aislamiento por adaptador |
| 3 | **Decisiones (1)** | 5:00-8:00 | A | 4 | MongoDB (perfil flexible, lectura por id, índice `equipo_id`), Neo4j (recorridos), Cassandra (partición `(partido, ventana de 10 min)`, escritura en ráfaga, consistencia eventual). Por base: consulta que la motivó → estructura → trade-off |
| 4 | **Decisiones (2)** | 8:00-11:00 | B | 4-5 | Redis (TTL, `noeviction` y su costo), InfluxDB (retención 7 d / 365 d, resumen 15 min), IRIS (herencia y relación padre-hijo; 8 licencias → pool de 5). Distribución propuesta y CAP: qué puede ser eventual y qué no |
| 5 | **Operación** | 11:00-14:00 | A + B | Pantalla 2 | Demo §1 de `demo.md`: seis requests, una por base. Cada uno dice qué base responde y **por qué esa estructura** (2 por persona + 2 de C) |
| 6 | **Evidencia** | 14:00-18:00 | C | Pantalla 2 + 6-7 | Grafana en vivo: disponibilidad en dos capas, latencia por base, errores. Falla controlada de Redis (demo §2, se lanza al empezar este bloque). Resultado: **47 → 138 req/s** con el corte rápido; 0 errores en las otras bases; alertas con impacto y acción |
| 7 | **Cierre** | 18:00-20:00 | A, B, C | 8 | Por qué la solución es adecuada (5 frases de `defensa_final.md`), trade-offs aceptados, qué mejoraríamos: más procesos de la API, réplicas, exporter de Cassandra |

## Reglas para respetar el tiempo

- La falla controlada corta se lanza **al comenzar el bloque 6** y dura ~3 min: se comenta mientras corre.
- Si a los 14:00 el bloque 5 no terminó, se saltean los requests de IRIS e InfluxDB (ya se vieron en la explicación).
- Si a los 18:00 la prueba no terminó, se muestra la captura `07_grafana_recuperacion.png` y se pasa al cierre.
- Preguntas: se responden con la tabla de [`../docs/defensa_final.md` §3](../docs/defensa_final.md#3-preguntas-que-la-fifa-podría-hacer-punto-65-y-respuestas-con-evidencia). Mostrar siempre **una evidencia** (panel, request, archivo), no solo la respuesta.

## Frases de apoyo (para no leer la pantalla)

- "No defendemos el código, defendemos **dónde vive cada dato y por qué**."
- "La caída de una base afecta **solo** a su parte del Fixture: lo medimos cuatro veces."
- "El monitoreo nos mostró un problema que no veíamos; lo corregimos y lo **volvimos a medir**."
- "Esto lo medimos; esto otro es una propuesta" (separar siempre).
