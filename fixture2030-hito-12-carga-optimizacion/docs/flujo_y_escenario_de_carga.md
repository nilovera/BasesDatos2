# Flujo seleccionado y escenario de carga

## 1. Flujo seleccionado (RF1, punto 5.1)

**"Consulta del partido en vivo"**: los hinchas abren la página de un partido alrededor del momento en que se juega y la aplicación pide, en paralelo, los datos que muestra esa pantalla. Es una parte integrada de la plataforma porque **una misma API** atiende pedidos que van a **las seis bases**.

| Aspecto | Definición |
|---|---|
| Quién genera la operación | Usuarios finales (hinchas) a través de la aplicación web/móvil, simulados por usuarios virtuales (VUs) |
| Punto de entrada | API REST integrada (FastAPI, Hito 10 + ajustes del Hito 11), `http://127.0.0.1:8000/api/v1` |
| Tipo de operación | **Lectura** (100 %). Ver justificación abajo |
| Respuesta esperada | HTTP 200 con el JSON del recurso, idéntico (huella) al relevado sin carga |
| Criterio de éxito | HTTP 200 **y** contenido igual a la huella del catálogo, dentro del timeout de 10 s |
| Errores y respuestas degradadas que se registran | código HTTP ≠ 200 (`http_4xx/5xx`, incluidos 503/504 de dependencias), `timeout`, errores de conexión, contenido `alterado` |

Operaciones del flujo y fuentes consultadas:

| Operación (endpoint) | Fuente | Qué lee | Peso en la mezcla |
|---|---|---|---:|
| `GET /partidos/{p}/comentarios?bucket_10min=…&limit=20` | Cassandra | 20 comentarios de una partición `(partido, bucket de 10 min)` | 30 % |
| `GET /partidos/{p}/estadisticas?desde&hasta&granularidad=detalle&equipo_id&limit=10` | InfluxDB 3 | 1 minuto de estadísticas cada 10 s de un equipo | 20 % |
| `GET /sesiones/{id}` | Redis | hash de la sesión + TTL | 15 % |
| `GET /partidos/{p}/eventos` | Neo4j | partido, equipos, sede y eventos (recorrido del grafo) | 15 % |
| `GET /partidos/{p}/detalle` | InterSystems IRIS | partido, árbitro y eventos (3 consultas SQL sobre objetos persistentes) | 10 % |
| `GET /equipos/{codigo}` | MongoDB | documento del equipo | 10 % |

**Por qué solo lecturas.** La API actual expone casi exclusivamente lecturas (la única escritura es `DELETE /sesiones/{id}`, que es destructiva y no tiene sentido repetir miles de veces). Además, el momento de mayor concurrencia del Fixture es la **lectura** masiva alrededor de un partido (Clase 13: "consulta previa al partido", "pico después del gol"). Agregar endpoints de escritura cambiaría el sistema que se quiere medir. La escritura masiva se probó en el Hito 6 (Cassandra, 44.652 filas/s con `COPY`).

**Volumen y frecuencia proyectados (no medidos):** según la Clase 13, 2–3 millones de usuarios simultáneos en el escenario, con picos de 90 minutos por partido. En el laboratorio se prueba una versión escalada (sección 2) y se explicita la diferencia.

## 2. Escenario de carga (RF2, punto 5.2)

Configuración: `config/configuracion-ejemplo.json` → `escenarios.completo`. Herramienta: `scripts/ejecutar_carga.py`.

| Elemento | Valor |
|---|---|
| Modelo | Cerrado: cada VU manda una solicitud, espera la respuesta, piensa 50–150 ms (uniforme) y repite |
| Cantidad inicial de datos | Catálogo de 1.895 claves (ver `datos-o-generadores/README.md`) |
| VUs | 5 → 40 → 80 → 10 según la fase |
| Tasa objetivo | No se fija una tasa: surge de VUs y tiempo de respuesta. Con respuesta de 20 ms, 40 VUs ≈ 330 req/s |
| Proporción lectura/escritura | 100 / 0 |
| Distribución de claves | 50 % a la clave caliente del partido en vivo (`PAR-0001`, `EQ-01`), 50 % uniforme |
| Generador | 4 procesos Python (asyncio + httpx); los VUs se reparten por `vu % 4`; todos siguen el mismo reloj de pared |
| Semilla | 2030 (cada VU: `2030 × 10000 + vu`) |
| Timeout por solicitud | 10 s |
| Muestreo de recursos | cada 2 s |

Fases:

| Fase | Duración | VUs | Se mide | Situación del Fixture que representa |
|---|---:|---|---|---|
| Calentamiento | 30 s | 5 | No (se descarta del global) | Conexiones, cachés del motor y JIT de drivers en frío |
| Rampa | 60 s | 5 → 40 | Sí | Consulta previa al partido, la gente entra de a poco |
| Sostenimiento | 180 s | 40 | Sí | Partido en curso |
| Pico post-gol | 30 s | 80 | Sí | Pico abrupto después de un gol |
| Recuperación | 30 s | 10 | Sí | Vuelta a la carga base: ¿el sistema se recupera? |
| **Total** | **330 s** | | | |

- **Condición de finalización:** fin de la última fase.
- **Interrupción segura:** si en los últimos 20 s falla más del 50 % de las solicitudes (con al menos 30 muestras), el proceso que lo detecta avisa a los demás y la prueba se corta. Ctrl+C también corta de forma ordenada y guarda lo medido.
- **Comportamiento ante timeout o error:** no se reintenta (un reintento escondería el error y duplicaría carga); la solicitud se registra como fallida con su causa y el VU sigue.
- **Limpieza / reutilización:** el escenario es de solo lectura, así que el ambiente queda igual y se puede repetir sin reinicializar. Antes de cada corrida se reinicia la API. Ver `limpiar_datos_de_prueba.py`.

Escenario `humo` (prueba de humo): 2 VUs durante 20 s, para verificar que todo el circuito funciona antes de la prueba larga.

## 3. Qué se mide y cómo (RF5, RF6, RNF5)

| Métrica | Unidad | Cómo se obtiene | Capa |
|---|---|---|---|
| Latencia (mín, prom, P50, P90, P95, P99, máx) | ms | `perf_counter` en el generador, desde antes del envío hasta tener la respuesta completa. Percentiles con interpolación lineal sobre todas las solicitudes exitosas de la fase | Generador (lo que ve el usuario) |
| Tiempo dentro de la API | ms | Encabezado `X-Process-Time-Ms` del middleware de la API (Hito 10) | API + adaptador + base |
| Throughput | solicitudes exitosas / s | exitosas de la fase ÷ duración real de la fase | Generador |
| Concurrencia | VUs activos | objetivo de la fase en cada instante (registrado por solicitud) | Generador |
| Errores | cantidad y % por causa | clasificación de cada solicitud | Generador |
| Integridad del contenido | ok / alterada / no verificable | huella SHA-256 de la respuesta vs. catálogo | Generador |
| CPU y RAM de la API | % de 1 núcleo, MB | `psutil` sobre el proceso de uvicorn y sus hijos | Sistema operativo |
| CPU y RAM del generador | % de 1 núcleo, MB | `psutil` sobre los 4 procesos generadores + el coordinador | Sistema operativo |
| Retraso del event loop del generador | ms | demora de un `sleep(0,1)` en cada proceso; si crece, el generador no da abasto | Generador |
| CPU y memoria de cada base | % / MiB | `docker stats --no-stream` cada 2 s | Productos NoSQL |
| CPU y RAM del sistema | % | `psutil` | Sistema operativo |

La diferencia **latencia del cliente − tiempo dentro de la API** es tiempo de cola antes del middleware (aceptación de la conexión, event loop de uvicorn) más red local y procesamiento del lado del generador. Esa diferencia fue la clave para detectar los dos cuellos de botella (ver `linea_base.md`).

Además, el log de la API registra cada `request_id` que manda el generador, lo que permite cruzar lo que el generador dice haber enviado con lo que la API dice haber atendido (`validar_integridad.py`).
