# Registro de los 17 puntos de la segunda revisión

Fecha: 20 de noviembre de 2026. La evidencia original fue una revisión estática; no una nueva ejecución de los motores. Crear este repo no cierra los pendientes de integración.

| ID | Punto | Evidencia | Estado actual | Aceptación |
|---|---|---|---|---|
| H01 | Equipos | EQ-xx frente a ARG/MEX y contratos distintos. | Catálogo y dos equivalencias definidos; propagación pendiente. | Consultar un mismo equipo en todos los motores con correspondencia explícita. |
| H02 | Jugadores | 1.024 IDs, nombres, posiciones y equipos coinciden entre generador MongoDB y carga Neo4j. | Correspondencia verificada estáticamente; datos cargados pendientes. | Comparación sobre los motores reales sin jugadores huérfanos. |
| H03 | Partidos | PAR-0001 representa rivales distintos en semillas históricas. | Catálogo de demostración unificado; migraciones pendientes. | Mismos rivales y fecha en todos los endpoints. |
| H04 | IRIS | La implementación histórica mantiene dependencias en código, configuración, arranque y diagnóstico. | API, Docker y métricas actuales no contienen dependencias de IRIS; se controla con pruebas. | Los cinco motores y pruebas integradas funcionan sin servicios, variables ni adaptadores de IRIS. |
| H05 | Versión base | monitoreo contiene mejoras posteriores a API. | Fuente seleccionada para reutilización; incorporación pendiente. | Conservar diagnóstico, aislamiento de fallos y métricas aplicables. |
| H06 | Ubicación Neo4j | Neo contiene MongoDB antiguo; scripts reales localizados dentro de monitoreo. | Origen identificado; incorporación pendiente. | Cargas Neo4j reproducibles desde el catálogo común. |
| H07 | Semillas MongoDB | El entorno consolidado histórico conserva nombres genéricos. | Carga idempotente validada; la recarga ya no pisa el estado operativo de partidos. | Preparar el entorno no sobrescribe catálogo ni agregados con eventos. |
| H08 | Eventos oficiales | Las semillas históricas asignan eventos contradictorios a PAR-0001, incluido un gol minuto 23 en IRIS. | Flujo oficial implementado en MongoDB con transacción y Outbox; ejecución API pendiente. | Un único evento oficial y proyecciones convergentes, sin depender de IRIS. |
| H09 | Pruebas Cassandra | Prueba consulta 203006131800; muestra carga 203006132000. | Pendiente. | Prueba reproducible de paginación con carga limpia. |
| H10 | Escrituras API | Faltan inicio, goles, correcciones, sustituciones y publicación de comentarios. | Inicio, gol, corrección y sustitución implementados; comentarios llegarán con Cassandra. | Ejecutar escrituras idempotentes y conflicto de clave en Docker. |
| H11 | Moderación | Lectura actual no distingue estados visibles, pendientes y ocultos. | Pendiente. | Consulta pública filtra adecuadamente y conserva paginación correcta. |
| H12 | Comentarios duplicados | CRUD escribe proyecciones por partido y por usuario en pasos separados. | Pendiente. | Recuperación y convergencia ante caída entre las dos escrituras. |
| H13 | Caché real | Script Redis simula las lecturas y cambios de MongoDB. | Pendiente. | Miss, carga real, hit, actualización e invalidación integrados. |
| H14 | Estadística individual | Generadores actuales producen estadísticas de equipo. | Pendiente. | Participaciones y sustituciones delimitan puntos y mapas de calor. |
| H15 | Paginación temporal | Estadísticas informa hay_mas sin cursor de continuación. | Pendiente. | Recorrer puntos con timestamp compartido sin omisiones ni repetición. |
| H16 | Validación documental | Las implementaciones históricas tenían reglas de almacenamiento más amplias que las de API. | OpenAPI, modelos Pydantic y validadores MongoDB usan el mismo vocabulario inicial. | Ejecutar rechazos incompatibles en API y almacenamiento. |
| H17 | Entorno y distribución | Los laboratorios históricos repiten nombres/puertos, usan volúmenes distintos y Cassandra RF1. | MongoDB, API, Prometheus y Grafana comparten red aislada y volúmenes propios; resto pendiente. | Entorno de cinco motores y pruebas de recuperación; réplicas demostradas por separado. |

