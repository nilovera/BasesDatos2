# Defensa final ante la FIFA (RF13 a RF16)

Grupo 10 · Luciano Corgnali, Nicolás Lovera, Valentino Sabignoso · Ingeniería de Datos II

> **Pregunta central:** ¿por qué esta combinación de modelos, estructuras, estrategias de distribución y mecanismos de observabilidad es adecuada para el Fixture Mundial 2030 bajo las condiciones planteadas?

## 1. Respuesta en cinco frases

1. El Fixture no es un solo tipo de dato: comentarios en ráfaga, relaciones entre partidos, sesiones que vencen, estadísticas cada 10 s, perfiles de equipos y objetos de partido. **Cada uno tiene un patrón de acceso que un modelo resuelve barato y otro resuelve caro** ([`decisiones_de_arquitectura.md`](decisiones_de_arquitectura.md) §1-2).
2. Por eso usamos **seis bases**, cada una fuente de verdad de un solo tipo de dato, integradas por **una API** que encapsula drivers, errores y conexiones (Hitos 4 a 10).
3. Lo comprobamos con carga y con fallas. Con 80 usuarios la API sostuvo ~330 req/s con 0 errores (Hito 12). Si cae una base, **solo** se afecta su porción del Fixture: 0 errores en las otras 5 bases en las 4 pruebas de falla (Hitos 11 y 13).
4. El monitoreo con Prometheus y Grafana no solo muestra que el sistema funciona: **nos mostró un problema que no veíamos**. Una base caída frenaba a todas (−65 % de throughput). Lo corregimos con el corte rápido y lo **volvimos a medir**: 138 req/s durante la falla, igual que sin falla.
5. La arquitectura no es perfecta. Cuesta operar seis productos, el laboratorio es de un nodo por base y Neo4j y Cassandra solo se observan desde afuera. Pero esos límites están **medidos o declarados**, y para cada uno hay una propuesta concreta.

## 2. Lo que se defiende de cada base (punto 6.4)

Los 10 puntos que pide la consigna para cada base (tipo de dato, consulta que motivó la elección, modelo, estructura, carga/recuperación, escala, consistencia, falla, trade-off y evidencia) están en **una sola tabla** en [`decisiones_de_arquitectura.md` §2](decisiones_de_arquitectura.md#2-cada-base-problema-patrón-estructura-distribución-y-evidencia). Durante la defensa se recorre esa tabla **por columna** (una base a la vez), con una demostración por base ([`../defensa/demo.md`](../defensa/demo.md)).

## 3. Preguntas que la FIFA podría hacer (punto 6.5) y respuestas con evidencia

| Pregunta | Respuesta corta | Evidencia |
|---|---|---|
| ¿Por qué eligieron este modelo para este tipo de dato? | Por la consulta dominante. Ejemplo: comentarios = "últimos N de un partido en una ventana": en Cassandra es **una partición** ordenada por fecha; no hay que filtrar ni ordenar | Esquema `comentarios_por_partido`; P95 ~24 ms |
| ¿Qué consulta sería costosa con otra estructura? | "Eventos del partido con equipos y sede" en documental: 3-4 lecturas resueltas en la aplicación. "Sesión vigente" en relacional: SELECT más una tarea que borre las vencidas | Hito 12, `comparacion_relacional.md` |
| ¿Cómo se distribuyen los datos? | Laboratorio: un nodo por base. Propuesta: Cassandra por partición `(partido, bucket)` replicada ×3 en cada región; Mongo y Neo4j con réplicas; Redis por región | `decisiones_de_arquitectura.md` §2-3 |
| ¿Qué sucede si se cae un nodo o una región? | Medido (un nodo): solo fallan las rutas de esa base, con 503 inmediato; el resto sigue. Propuesto (región): comentarios y estadísticas siguen en las otras regiones (AP); resultados y sesiones esperan al primario (CP) | Pruebas de falla; tabla CAP §3 |
| ¿Qué garantía de consistencia necesita este módulo? | Resultado y eventos: fuerte. Sesión cerrada: fuerte por clave. Comentarios y estadísticas en vivo: eventual | §2, fila "Consistencia" |
| ¿Qué parte de la respuesta puede ser eventual? | Comentarios (pueden aparecer 1 s más tarde) y estadísticas en vivo | §3 |
| ¿Dónde se encuentra el cuello de botella? | En la **API** (un solo proceso): 70-86 % de CPU con 40-80 usuarios en el Hito 12. Entre las bases, la más lenta es Cassandra (P95 ~24 ms), muy lejos del límite | Panel "CPU del proceso de la API"; Hito 12 |
| ¿Cómo distinguen que el problema está en la API y no en la base? | Si sube la latencia de **todas** las bases y la CPU de la API → API. Si sube **una** base y su ping → esa base. Puerto OK pero ping falla → configuración o motor que no arrancó | `decisiones_de_arquitectura.md` §5; incidente de IRIS |
| ¿Qué métrica observarían primero ante un aumento de latencia? | "Latencia P95 por base" (ubica el motor), después "CPU del proceso de la API" | Dashboard, secciones 3 y 6 |
| ¿Qué evidencia tienen de que la optimización funcionó? | Corte rápido: 47 → 138 req/s durante la falla, P95 de Redis 2.812 → 4,9 ms, mismo escenario. Pool de IRIS: −84 % (Hito 12) | `evidencia/comparacion_corte_rapido.md` |
| ¿Qué cambiarían si el tráfico se multiplica? | 1) Varios procesos/instancias de la API (primer límite). 2) Repartir las 8 licencias de IRIS o pasar a Enterprise. 3) Réplicas de lectura en Mongo y Neo4j. 4) Cassandra con más nodos: su modelo ya particiona por partido | §7 |
| ¿Qué se perdería o retrasaría durante una falla? | Con Redis caído: no se validan sesiones durante la falla (se midieron 832-2.492 respuestas 503), pero no se perdió ningún dato (huellas idénticas). Comentarios en una región caída: llegan tarde | `integridad_datos_*.json` |
| ¿Qué información no pueden afirmar porque no fue medida? | Comportamiento con varios nodos o regiones, métricas internas de Neo4j y Cassandra, carga real de un Mundial, variación entre corridas del corte rápido (una por versión) | `limitaciones_y_evidencia.md` §1-3 |
| ¿Qué costo operativo agrega mantener seis modelos? | Seis motores que operar, seis lenguajes, seis formas de monitorear y fallas de entorno (incidente real de IRIS). Se mitiga con la API, `entorno-local`, scripts idempotentes y una capa común de monitoreo | `decisiones_de_arquitectura.md` §9 |
| ¿Por qué NO usaron SQL? | No es "NoSQL siempre": un relacional daría ACID y claves foráneas (habría evitado inconsistencias que encontró el Data Mart). Pero concentra en un motor las ráfagas de comentarios, necesita tareas para vencer sesiones y particiones manuales para series temporales. Para la **analítica** sí proponemos un modelo relacional (Data Mart) | Hito 12 |
| ¿Cómo escala Cassandra en un pico de gol? | Las escrituras se reparten por partición `(partido, bucket de 10 min)`: un gol en un partido escribe en una sola partición caliente por 10 min, que se replica en N nodos. Si un partido concentrara demasiado, se achica el bucket | Hito 6; propuesta |

## 4. Qué demuestra el monitoreo (y qué no)

| Demuestra (medido) | No demuestra |
|---|---|
| Que los 9 jobs esperados se recolectan (14 targets) | Que el sistema aguante el tráfico real de un Mundial |
| Disponibilidad, latencia, volumen y errores por base, en el tiempo | Lo que pasa dentro de Neo4j y Cassandra |
| Que una falla se detecta en 4-30 s y alerta en ~1,5 min | Comportamiento con réplicas o particiones de red |
| Que una base caída no produce errores en las demás | — |
| Que una mejora funcionó (antes/después en el mismo escenario) | — |

## 5. Cierre

Proponemos esta solución porque **cada base está donde su patrón de acceso es barato**, porque **una falla queda acotada a su módulo** (medido), y porque el monitoreo nos permite **ver, explicar y corregir** el comportamiento del sistema con números. Los trade-offs que aceptamos (costo operativo, consistencia eventual en comentarios, licencias de IRIS) están identificados y cada uno tiene una alternativa propuesta para la siguiente iteración.
