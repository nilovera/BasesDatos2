# Fixture 2030 — Patrones de acceso y requisitos de datos

**Estado:** documento vivo  
**Versión:** 1.0  
**Fecha de actualización:** 30 de octubre de 2026  
**Documento relacionado:** `alcance_funcional_fixture2030.md`  
**Objetivo:** definir qué necesita cada funcionalidad antes de comparar y seleccionar motores de datos.

---

## 1. Propósito de esta etapa

Esta etapa traduce el alcance funcional de Fixture 2030 a requisitos técnicos y operativos.

Todavía no se selecciona una base de datos definitiva. Primero se definen:

- Consultas principales.
- Operaciones de escritura.
- Claves conocidas al acceder a los datos.
- Volumen y velocidad de crecimiento.
- Frecuencia de actualización.
- Objetivos de latencia.
- Modelo de consistencia requerido.
- Importancia de la durabilidad.
- Retención.
- Posibles criterios de distribución.
- Comportamiento esperado ante fallos.

Este orden evita elegir una tecnología solamente por el volumen o por lo ya implementado en los hitos. La elección posterior deberá justificarse por el patrón de acceso dominante y por los trade-offs aceptados.

---

## 2. Principios de análisis

### 2.1 Diseñar desde las consultas

Una misma entidad puede necesitar representaciones diferentes si existen consultas dominantes distintas. Antes de diseñar una tabla, documento, grafo o serie temporal se debe conocer:

1. Qué pregunta se quiere responder.
2. Qué datos de entrada se conocen.
3. Cuántos resultados se esperan.
4. Con qué frecuencia se ejecuta.
5. Qué costo tendría una respuesta atrasada o incorrecta.

No se debe intentar resolver todas las consultas con una única estructura universal.

### 2.2 Separar lectura, escritura y derivación

Para cada módulo se distinguirán:

- **Datos originales:** ingresados por una persona, proveedor o sistema.
- **Datos oficiales:** aceptados como estado válido del negocio.
- **Datos derivados:** calculados desde información oficial.
- **Datos temporales:** útiles durante un período corto.
- **Proyecciones de lectura:** copias optimizadas para una consulta concreta.

### 2.3 La consistencia no es igual para todo

Se utilizarán estas categorías:

| Modelo | Interpretación en Fixture 2030 |
|---|---|
| Fuerte | Una lectura debe obtener el último estado confirmado o fallar. |
| Causal | Los cambios relacionados deben observarse en orden lógico. Por ejemplo, un partido debe existir antes que sus eventos. |
| De sesión | El usuario debe ver inmediatamente su propia operación durante la misma sesión. |
| Eventual | Se admite una demora breve mientras las copias convergen. |

### 2.4 La durabilidad tampoco es igual para todo

| Nivel | Consecuencia aceptable |
|---|---|
| Crítica | La operación confirmada no puede perderse. |
| Alta | Debe conservarse; puede recuperarse mediante reintentos o reprocesamiento. |
| Media | Puede reconstruirse desde una fuente oficial. |
| Baja | Puede descartarse o recrearse sin afectar el historial del negocio. |

### 2.5 Laboratorio y arquitectura objetivo

| Escenario | Significado |
|---|---|
| Prueba de concepto | Contenedores locales, datos simulados y una instancia por motor. Permite comprobar modelos, API y consultas. |
| Arquitectura objetivo | Diseño distribuido con replicación, particionado, recuperación y tolerancia a fallos. No se presenta como capacidad ya validada. |

---

## 3. Supuestos de trabajo

### 3.1 Datos ya demostrados en los hitos

- 64 equipos.
- 1024 jugadores.
- 96 partidos en el conjunto de grafos utilizado.
- Estadísticas de un partido tomadas cada 10 segundos.
- 1080 puntos detallados para dos equipos durante 90 minutos.
- 12 resúmenes de 15 minutos para ese partido.
- Sesiones temporales con expiración.
- Comentarios consultados por partido y ventana temporal.

Estos valores describen la prueba académica, no el límite máximo de la plataforma.

### 3.2 Escala objetivo pendiente

La cátedra todavía no indicó en este trabajo una cifra obligatoria de:

- Usuarios concurrentes.
- Solicitudes por segundo.
- Partidos simultáneos.
- Comentarios por segundo.
- Regiones geográficas.
- Objetivo de disponibilidad.

Hasta validarlo, el diseño utilizará:

- Clasificaciones cualitativas de volumen.
- Fórmulas de crecimiento.
- Objetivos de latencia propuestos, no resultados medidos.
- Una pregunta explícita para el profesor.

### 3.3 Objetivos iniciales de latencia

Estos valores son propuestas para guiar el diseño y deberán validarse:

| Operación | Objetivo inicial |
|---|---:|
| Lectura del estado en vivo | Menos de 200 ms |
| Lectura de catálogo | Menos de 500 ms |
| Publicación y lectura de comentarios | Menos de 500 ms |
| Confirmación de una escritura oficial | Menos de 1 segundo, sin sacrificar durabilidad |
| Consulta histórica o analítica | Menos de 2 segundos para rangos acotados |

La latencia de la prueba local no demuestra que estos objetivos se cumplan en producción.

---

# 4. Bloque 1 — Núcleo oficial

## 4.1 Fixture y partidos

| Criterio | Análisis |
|---|---|
| Lecturas principales | Partido por código; partidos por fecha; partidos por equipo; partidos por fase, grupo o llave; partido por sede; estado y marcador actual; próximos partidos; cruces de eliminación. |
| Escrituras | Programación, reprogramación, asignación de equipos, sede y árbitro; cambios válidos de estado; actualización del marcador; inicio, suspensión, reanudación, finalización o cancelación. |
| Claves de acceso | `partido_id`, fecha, equipo, fase, grupo, sede y estado. |
| Volumen | Bajo. Decenas o cientos de partidos por competencia. El volumen no justifica por sí solo una tecnología distribuida. |
| Frecuencia | Programación poco frecuente; durante el partido cambia ante inicio, goles, suspensión, reanudación y finalización. |
| Latencia | Muy baja para el estado visible; moderada para consultas históricas. Objetivo propuesto: menos de 200 ms en vivo. |
| Consistencia | Fuerte para estado, participantes y marcador oficial. No se debe mostrar un partido finalizado como activo ni aceptar dos estados incompatibles. |
| Durabilidad | Crítica. Un cambio confirmado del estado oficial no puede perderse. |
| Retención | Permanente durante toda la vida de la competencia y su consulta histórica. |
| Distribución | Candidato lógico: competencia o temporada. En la escala académica no hace falta fragmentar agresivamente. Las lecturas globales del fixture deben seguir siendo eficientes. |
| Fallo | Se puede servir temporalmente el último estado confirmado con una marca de posible desactualización. No se deben aceptar cambios oficiales si no pueden persistirse de manera durable. |

### Reglas adicionales

- Las transiciones de estado deben ser válidas.
- Cada comando debe ser idempotente.
- El mismo mensaje del proveedor no debe iniciar o finalizar dos veces el partido.
- El orden por partido debe preservarse.
- El marcador debe poder reconstruirse a partir de eventos oficiales o reconciliarse con ellos.
- Debe registrarse la versión del partido para detectar actualizaciones concurrentes.

### Preguntas de negocio dominantes

1. ¿Cuál es el estado y marcador actual de `PAR-0001`?
2. ¿Qué partidos juega un equipo durante una fase?
3. ¿Qué partidos se disputan en una fecha o sede?
4. ¿De qué partidos anteriores provienen los equipos de una llave eliminatoria?

## 4.2 Alineaciones

| Criterio | Análisis |
|---|---|
| Lecturas principales | Alineación completa por partido y equipo; titulares; suplentes; jugador y posición; alineación activa en un instante. |
| Escrituras | Recepción de la alineación; confirmación; corrección previa al inicio; cambio excepcional autorizado. |
| Claves de acceso | `partido_id + equipo_id`; secundariamente `jugador_id + partido_id`. |
| Volumen | Bajo a medio. Aproximadamente una convocatoria por equipo y partido. |
| Frecuencia | Se carga antes del partido y cambia muy pocas veces. Después de confirmarse debe considerarse estable. |
| Latencia | Menos de 500 ms en consulta; la confirmación puede priorizar validación sobre velocidad. |
| Consistencia | Fuerte al confirmar. Un jugador no puede aparecer simultáneamente como titular y suplente del mismo equipo. |
| Durabilidad | Crítica porque determina participación, sustituciones, minutos y mapas de calor. |
| Retención | Permanente junto con el historial del partido. |
| Distribución | Por partido y equipo. La alineación completa debe recuperarse con una consulta acotada. |
| Fallo | Puede mostrarse la última alineación confirmada. Una nueva confirmación debe fallar o quedar pendiente si no puede persistirse de forma segura. |

### Reglas adicionales

- La confirmación debe ser idempotente.
- Los jugadores deben pertenecer a la convocatoria válida del equipo.
- Debe distinguirse borrador de alineación confirmada.
- Una corrección posterior debe conservar historial y responsable.

## 4.3 Sustituciones

| Criterio | Análisis |
|---|---|
| Lecturas principales | Sustituciones por partido; sustituciones por equipo; historial de participación de un jugador; quién estaba en cancha en un minuto. |
| Escrituras | Ingreso del evento de sustitución; cierre del intervalo del jugador saliente; apertura del intervalo del ingresante; corrección o anulación. |
| Claves de acceso | `partido_id`; `partido_id + equipo_id`; `jugador_id + partido_id`. |
| Volumen | Bajo. Pocos eventos por equipo y partido. |
| Frecuencia | Esporádica durante el partido. |
| Latencia | Debe reflejarse en segundos porque afecta seguimiento, minutos y mapas de calor. |
| Consistencia | Fuerte y causal. El jugador saliente debe estar en cancha y el ingresante debe estar habilitado. El cierre debe ocurrir antes de abrir una participación incompatible. |
| Durabilidad | Crítica. Una sustitución oficial confirmada no puede perderse. |
| Retención | Permanente. |
| Distribución | Por partido; proyección adicional por jugador si la consulta histórica lo requiere. |
| Fallo | No se debe confirmar la sustitución si no se puede guardar oficialmente. Las proyecciones estadísticas pueden actualizarse después mediante reintentos. |

### Idempotencia

El proveedor debe enviar un identificador único. Si se recibe dos veces la misma sustitución, el sistema devolverá el resultado previamente confirmado sin duplicar intervalos ni eventos.

## 4.4 Eventos oficiales

| Criterio | Análisis |
|---|---|
| Lecturas principales | Timeline por partido; eventos por tipo; eventos de un equipo o jugador; último evento; goles y tarjetas; eventos dentro de un período. |
| Escrituras | Alta de evento, corrección, anulación o evento compensatorio. Actualización derivada del marcador o disciplina. |
| Claves de acceso | `partido_id + tiempo`; `evento_id`; secundariamente equipo, jugador y tipo. |
| Volumen | Bajo o medio por partido, pero de alto valor. El tráfico masivo se concentra en las lecturas, no en la cantidad de eventos oficiales escritos. |
| Frecuencia | Irregular durante el partido. Puede haber ráfagas, pero no miles de eventos oficiales por segundo en un mismo partido. |
| Latencia | Lectura muy baja durante el partido. La escritura puede tardar algo más para asegurar validación y durabilidad. |
| Consistencia | Fuerte para la aceptación oficial; causal para mantener el orden del partido; eventual solo para copias de lectura y métricas derivadas. |
| Durabilidad | Crítica. Un gol o tarjeta confirmados no pueden residir únicamente en una capa temporal. |
| Retención | Permanente. Las correcciones deben conservar el original y su historial. |
| Distribución | Por partido. Si una competencia genera particiones demasiado grandes, se puede incorporar período o bucket, manteniendo la consulta cronológica. |
| Fallo | Si la persistencia oficial no está disponible, el evento no debe confirmarse. Las capas de lectura pueden servir el último timeline confirmado e informar desactualización. |

### Requisitos especiales

- Identificador idempotente proporcionado o generado al recibir el evento.
- Secuencia o versión por partido.
- Timestamp del proveedor y timestamp de recepción.
- Estado: recibido, validado, confirmado, corregido o anulado.
- Reconciliación entre marcador y goles.
- Auditoría de toda corrección.
- Capacidad de reprocesar proyecciones sin modificar el registro oficial.

---

# 5. Bloque 2 — Información en vivo

## 5.1 Estadísticas de equipos

| Criterio | Análisis |
|---|---|
| Lecturas principales | Evolución de posesión, pases, tiros, córners, faltas y recuperaciones; comparación entre equipos; ventana temporal; último valor; resumen por intervalo. |
| Escrituras | Inserción periódica de mediciones y generación de agregados. Las mediciones se agregan, no se actualizan continuamente sobre una única fila histórica. |
| Claves de acceso | `partido_id + equipo_id + timestamp`; intervalo temporal. |
| Volumen | Alto y predecible. Con dos equipos, 90 minutos y una muestra cada 10 segundos: `2 × 90 × 6 = 1080` puntos por partido. |
| Frecuencia | Una medición cada 10 segundos por equipo en la prueba académica. |
| Latencia | El último dato debería estar visible pocos segundos después de recibido. Las consultas históricas pueden tolerar más latencia. |
| Consistencia | Eventual. Una demora breve es aceptable, pero la serie no debe retroceder ni mezclar partidos. |
| Durabilidad | Alta para agregados; media para datos detallados si el proveedor permite replay. |
| Retención | Propuesta ya aplicada: detalle por 7 días y agregados por 365 días. Debe confirmarse para el trabajo final. |
| Distribución | Partido, equipo y rango temporal. Evitar una única partición global de estadísticas. |
| Fallo | La consulta puede devolver el último valor y su timestamp. Las mediciones no procesadas deben reintentarse o reproducirse desde el proveedor. |

### Calidad de datos

- Detección de muestras duplicadas.
- Identificación de huecos temporales.
- Uso consistente de UTC.
- Unidad y precisión documentadas.
- Agregados reproducibles desde los datos detallados mientras estos existan.

## 5.2 Estadísticas de jugadores

| Criterio | Análisis |
|---|---|
| Lecturas principales | Estadísticas de un jugador en un partido; comparación; evolución por período; acumulado por fase o torneo; últimos valores. |
| Escrituras | Muestras periódicas y actualizaciones derivadas de eventos: pases, tiros, asistencias, recuperaciones, distancia y velocidad. |
| Claves de acceso | `partido_id + jugador_id + timestamp`; jugador, equipo, fase y torneo para acumulados. |
| Volumen | Alto. Como orden inicial: `jugadores en cancha × 540 muestras`. Con 22 jugadores y frecuencia de 10 segundos, son aproximadamente 11.880 muestras por partido, sin contar cambios de participación. |
| Frecuencia | Cada 10 segundos para datos temporales; inmediata o por micro-lotes para métricas derivadas de eventos. |
| Latencia | Pocos segundos durante el partido; hasta 2 segundos para consultas acumuladas acotadas. |
| Consistencia | Eventual para métricas en vivo. Los goles y asistencias deben reconciliarse con eventos oficiales. |
| Durabilidad | Alta para acumulados; media para muestras crudas reproducibles. |
| Retención | Detalle temporal limitado; acumulados por partido y torneo conservados a largo plazo. La duración exacta queda pendiente. |
| Distribución | Partido y jugador, con tiempo como orden. Los acumulados pueden distribuirse por competencia y jugador. |
| Fallo | Mostrar el último corte disponible y su timestamp. Reprocesar cuando se recupere la fuente. No inventar valores faltantes. |

### Dependencias funcionales

- Minutos jugados dependen de alineaciones y sustituciones.
- Goles y asistencias dependen de eventos oficiales.
- Distancia y velocidad dependen de datos posicionales.
- Los acumulados deben poder recalcularse.

## 5.3 Mapas de calor

| Criterio | Análisis |
|---|---|
| Lecturas principales | Mapa por jugador y partido; filtro por período; comparación de períodos; puntos o celdas agregadas; mapa de titulares y suplentes. |
| Escrituras | Coordenadas X/Y, velocidad, período y timestamp mientras el jugador está en cancha. Generación posterior de celdas agregadas. |
| Claves de acceso | `partido_id + jugador_id + timestamp`; período; celda espacial para agregados. |
| Volumen | Muy alto respecto del catálogo. Con 22 jugadores activos y muestra cada 10 segundos: aproximadamente 11.880 posiciones por partido. Una frecuencia mayor multiplicaría linealmente el volumen. |
| Frecuencia | Cada 10 segundos en el alcance académico. No se afirma seguimiento GPS por segundo. |
| Latencia | El mapa en vivo puede actualizarse cada varios segundos. El mapa final puede generarse después del partido. |
| Consistencia | Eventual. Debe respetarse causalmente el intervalo de participación del jugador. |
| Durabilidad | Media para coordenadas crudas si pueden reproducirse; alta para el mapa agregado final y métricas consolidadas. |
| Retención | Coordenadas crudas con retención limitada; celdas agregadas e indicadores finales con retención prolongada. |
| Distribución | Partido y jugador; subdivisión temporal si el volumen crece. |
| Fallo | Se mantiene el mapa hasta el último punto recibido. Los huecos se señalan y no deben completarse como si fueran mediciones reales. |

### Validaciones

- Coordenadas dentro de los límites del campo.
- Timestamp dentro del intervalo del partido.
- Jugador habilitado y en cancha.
- Equipo consistente con la alineación.
- Rechazo o aislamiento de puntos duplicados o fuera de orden.

## 5.4 Rankings

| Criterio | Análisis |
|---|---|
| Lecturas principales | Máximo goleador, asistidor, pases completados, recuperaciones, tiros al arco y distancia; filtros por partido, equipo, grupo, fase o torneo. |
| Escrituras | Actualización de posiciones a partir de eventos y estadísticas; recálculo completo cuando existe una corrección. |
| Claves de acceso | Tipo de ranking + alcance; jugador como integrante ordenado. |
| Volumen | Bajo en cantidad de filas, pero con muchas lecturas durante y después de los partidos. |
| Frecuencia | Se actualiza ante cada evento relevante o por intervalos cortos. |
| Latencia | Muy baja para lectura. Se admite una demora de pocos segundos. |
| Consistencia | Eventual. Después de una corrección oficial debe converger al valor correcto. |
| Durabilidad | Media, porque puede reconstruirse desde eventos y estadísticas consolidadas. |
| Retención | Permanente por competencia, con histórico de ediciones si se desea. |
| Distribución | Por competencia, tipo de ranking y alcance. |
| Fallo | Puede devolverse el ranking anterior con su fecha de cálculo. Si se pierde, debe reconstruirse desde las fuentes. |

### Reglas de desempate

Antes de implementar se deberán acordar reglas para cada ranking. Ejemplo para goleadores:

1. Mayor cantidad de goles.
2. Menor cantidad de minutos jugados.
3. Menor cantidad de penales, si la competencia lo utiliza.
4. Orden estable por identificador como último criterio técnico.

Las reglas deportivas definitivas deben validarse con el profesor o declararse como supuesto.

---

# 6. Bloque 3 — Usuarios e interacción

## 6.1 Equipos y jugadores como catálogo

| Criterio | Análisis |
|---|---|
| Lecturas principales | Equipo o jugador por código; equipos por confederación; jugadores por equipo o posición; plantel; convocatoria; ranking. |
| Escrituras | Alta inicial, actualización de datos descriptivos, cambio de ranking, club, dorsal o convocatoria. |
| Claves de acceso | Código de equipo o jugador; confederación; equipo; posición; nombre normalizado. |
| Volumen | Bajo en la competencia académica: 64 equipos y 1024 jugadores. |
| Frecuencia | Lecturas frecuentes; escrituras poco frecuentes. |
| Latencia | Menos de 500 ms. Puede utilizarse una copia temporal para lecturas repetidas, pero no es un requisito de propiedad del dato. |
| Consistencia | Eventual para datos descriptivos; más fuerte para identidad, código y pertenencia a la convocatoria. |
| Durabilidad | Alta. Constituye información maestra del torneo. |
| Retención | Permanente o por edición, conservando historia relevante. |
| Distribución | En la escala académica no necesita fragmentación. Si creciera globalmente, puede distribuirse por código o región manteniendo unicidad. |
| Fallo | Se puede servir una copia desactualizada por un período limitado. Las modificaciones administrativas deben esperar a que la fuente maestra esté disponible. |

### Observación

La existencia de relaciones con partidos o eventos no obliga a que el catálogo principal se modele como grafo. Las proyecciones se decidirán posteriormente según las consultas de navegación reales.

## 6.2 Usuarios

| Criterio | Análisis |
|---|---|
| Lecturas principales | Perfil por identificador; preferencias; equipo favorito; rol; estado de cuenta. |
| Escrituras | Alta, modificación de perfil, preferencias, rol, estado y configuración de notificaciones. |
| Claves de acceso | `usuario_id`; correo normalizado como identificador único; eventualmente equipo favorito. |
| Volumen | Potencialmente alto y creciente. No está limitado por la cantidad de participantes del torneo. |
| Frecuencia | Lecturas frecuentes al iniciar una sesión; actualizaciones poco frecuentes. |
| Latencia | Menos de 500 ms. |
| Consistencia | Fuerte para identificador, correo único, rol y estado; de sesión para preferencias modificadas por el propio usuario. |
| Durabilidad | Alta. El perfil no puede depender de la duración de una sesión. |
| Retención | Mientras la cuenta esté activa y durante el período definido para bajas. La política exacta queda fuera del alcance académico. |
| Distribución | Por identificador de usuario. Deben evitarse particiones por país si generan desequilibrio. |
| Fallo | Las funciones públicas continúan. No se aceptan cambios de perfil o roles si no pueden persistirse. Puede mantenerse una sesión existente según su política. |

### Datos sensibles

El alcance no incluye guardar contraseñas reales ni información de pago. Correo, país y preferencias deben tratarse como datos personales y no exponerse en logs o auditorías sin necesidad.

## 6.3 Sesiones

| Criterio | Análisis |
|---|---|
| Lecturas principales | Validación por token o identificador; usuario y rol; último acceso; partido actual; tiempo de expiración. |
| Escrituras | Creación, renovación, actualización de actividad, cambio de partido actual y cierre. |
| Claves de acceso | Identificador de sesión conocido. |
| Volumen | Proporcional a usuarios conectados. Alto durante partidos importantes. |
| Frecuencia | Muy alta: validación por solicitud y renovación periódica. |
| Latencia | Muy baja; objetivo orientativo menor a 50 ms dentro de la infraestructura. |
| Consistencia | Fuerte dentro de la sesión. Un cierre o expiración debe impedir nuevas acciones inmediatamente o dentro de una ventana explícita mínima. |
| Durabilidad | Baja o media. Perder una sesión obliga a reautenticarse, pero no debe perder el perfil. |
| Retención | Temporal mediante TTL. La prueba académica utilizó 30 minutos como ejemplo. |
| Distribución | Hash del identificador de sesión para balancear carga. |
| Fallo | La política debe ser segura: si no se puede validar una sesión para una operación protegida, se rechaza. Las consultas públicas siguen funcionando. |

### Requisitos adicionales

- Tokens no registrados en texto plano en logs.
- Expiración automática.
- Revocación explícita.
- Renovación controlada.
- El caché de un perfil no reemplaza su fuente permanente.

## 6.4 Comentarios

| Criterio | Análisis |
|---|---|
| Lecturas principales | Comentarios recientes por partido; ventana temporal; comentarios por usuario; paginación cronológica; contenido oculto para administración. |
| Escrituras | Publicar, ocultar, cambiar estado de moderación, registrar likes y opcionalmente respuestas o menciones. |
| Claves de acceso | `partido_id + bucket_temporal`; `usuario_id + día`; identificador de comentario. |
| Volumen | Muy alto y variable. Puede presentar ráfagas después de goles o decisiones arbitrales. |
| Frecuencia | Escrituras y lecturas concurrentes durante partidos. |
| Latencia | Menos de 500 ms para publicar y leer la ventana reciente. |
| Consistencia | Eventual entre regiones; de sesión para que el autor vea su comentario; causal si existen respuestas. Likes pueden converger eventualmente. |
| Durabilidad | Alta para comentarios aceptados, aunque una demora de propagación sea admisible. |
| Retención | Durante la competencia y un período histórico. El TTL definitivo debe validarse. Contenido eliminado legalmente debe seguir una política específica. |
| Distribución | Por partido y ventana de tiempo para evitar particiones calientes ilimitadas; proyección separada por usuario para esa consulta. |
| Fallo | Puede aceptarse temporalmente en una cola durable o rechazarse con reintento. No debe confirmarse si solo quedó en memoria. La lectura puede mostrar la última ventana disponible. |

### Paginación

Se utilizará paginación por cursor o estado de página. No se recomienda paginación por desplazamientos grandes porque su costo crece y puede producir resultados inestables durante nuevas escrituras.

### Moderación

No existe un rol independiente de moderador. El administrador puede ocultar contenido. El cambio debe conservarse en auditoría.

---

# 7. Bloque 4 — Componentes transversales

## 7.1 Auditoría

| Criterio | Análisis |
|---|---|
| Lecturas principales | Operaciones por recurso, usuario, servicio, request ID y rango temporal; cambios rechazados; historial de un evento o partido. |
| Escrituras | Registros append-only de cambios oficiales, correcciones, moderación, roles, autorizaciones y operaciones administrativas. |
| Claves de acceso | Servicio + fecha; recurso + identificador; request ID. Pueden requerirse proyecciones distintas. |
| Volumen | Alto y continuo. Crece con todas las operaciones relevantes, no solo con partidos. |
| Frecuencia | Escritura sostenida; lectura poco frecuente salvo incidentes o controles. |
| Latencia | La escritura no debe agregar una demora excesiva al negocio. Las consultas pueden tolerar segundos. |
| Consistencia | Orden causal por recurso. No es necesario un orden global de toda la plataforma. |
| Durabilidad | Crítica. No debe perderse silenciosamente una auditoría confirmada. |
| Retención | Reciente consultable y archivo histórico de largo plazo. El plazo exacto debe definirse como política, no inventarse como requisito legal. |
| Distribución | Por servicio y bucket diario o mensual; proyecciones por recurso o request ID cuando sean consultas obligatorias. |
| Fallo | La operación de negocio no debería perderse por una falla momentánea de la proyección de auditoría, pero debe existir un registro durable pendiente que permita completar la auditoría después. |

### Diferencia frente a logs

- El log técnico ayuda a diagnosticar ejecución.
- La auditoría explica quién o qué servicio cambió un recurso, qué resultado obtuvo y cómo evolucionó el negocio.
- Los logs pueden rotarse; la auditoría sigue una política de conservación explícita.

## 7.2 Multimedia

| Criterio | Análisis |
|---|---|
| Lecturas principales | Metadatos y URL por recurso; highlights de un partido o evento; recursos de un jugador; disponibilidad y derechos. |
| Escrituras | Alta o actualización de metadatos; asociación con partido, evento o jugador; cambio de estado o derechos; checksum. |
| Claves de acceso | Recurso, partido, evento, jugador y tipo. El archivo se accede mediante una clave de objeto o URL. |
| Volumen | Bajo o medio en cantidad de metadatos; muy alto en bytes si se almacenaran videos. |
| Frecuencia | Escrituras poco frecuentes; lecturas con picos después de eventos importantes. |
| Latencia | Metadatos por debajo de 500 ms. La entrega del archivo depende del almacenamiento externo o CDN. |
| Consistencia | Eventual para publicación; fuerte para derechos, estado de disponibilidad y eliminación. |
| Durabilidad | Alta para archivos y metadatos publicados. |
| Retención | Prolongada, sujeta a derechos. |
| Distribución | Metadatos por identificador; objetos por clave y región. |
| Fallo | La plataforma principal sigue operando. Se informa que el contenido multimedia no está disponible sin afectar fixture, eventos o estadísticas. |

### Límite de implementación

La entrega implementará, como máximo, metadatos y URLs simuladas. El almacenamiento de objetos y la CDN se documentarán como arquitectura objetivo.

## 7.3 API REST

| Criterio | Análisis |
|---|---|
| Lecturas principales | Todas las consultas públicas y protegidas de los módulos anteriores. |
| Escrituras | Comandos del proveedor, operaciones del usuario y acciones administrativas. |
| Claves de acceso | Recursos REST, parámetros, cursor y request ID. |
| Volumen | Suma del tráfico de todos los módulos. Los picos se concentran en partidos importantes. |
| Frecuencia | Continua; debe escalar horizontalmente sin conservar estado local indispensable. |
| Latencia | Debe asignar presupuestos de tiempo por endpoint y dependencia. No todas las consultas deben compartir el mismo timeout. |
| Consistencia | La API debe expresar la garantía del recurso, no ocultarla. Una respuesta puede incluir timestamp, versión o estado de actualización. |
| Durabilidad | La API no es almacenamiento. Debe confirmar una escritura solamente después de cumplir la durabilidad exigida por el caso de uso. |
| Retención | Request IDs y trazas según política; nunca secretos o tokens en logs. |
| Distribución | Instancias sin estado detrás de balanceo; la sesión se administra externamente. |
| Fallo | Degradación aislada: la caída de multimedia o comentarios no debe impedir consultar fixture. Las operaciones dependientes de un motor caído devuelven un error controlado. |

### Requisitos comunes de la API

- Versionado, por ejemplo `/api/v1`.
- Validación de entrada.
- Errores consistentes.
- `request_id` por solicitud.
- Timeouts por dependencia.
- Paginación por cursor en colecciones grandes.
- Idempotency key para escrituras del proveedor.
- Autenticación simulada dentro del alcance académico.
- Autorización por rol.
- Límites de tamaño.
- No exponer credenciales ni detalles internos.
- Health checks separados de readiness.
- Métricas por endpoint y dependencia.

---

# 8. Matriz consolidada

| Funcionalidad | Volumen | Escritura | Consistencia dominante | Durabilidad | Retención |
|---|---|---|---|---|---|
| Fixture y partidos | Bajo | Baja | Fuerte | Crítica | Permanente |
| Alineaciones | Bajo | Baja | Fuerte | Crítica | Permanente |
| Sustituciones | Bajo | Baja y esporádica | Fuerte y causal | Crítica | Permanente |
| Eventos oficiales | Bajo/medio | Irregular | Fuerte al confirmar | Crítica | Permanente |
| Estadísticas de equipos | Alto | Periódica | Eventual | Alta/media | Detalle limitado; agregados prolongados |
| Estadísticas de jugadores | Alto | Periódica | Eventual con reconciliación | Alta/media | Detalle limitado; acumulados prolongados |
| Mapas de calor | Muy alto | Periódica | Eventual y causal con participación | Media/alta | Crudo limitado; agregado prolongado |
| Rankings | Bajo | Derivada | Eventual | Media/reconstruible | Permanente por torneo |
| Equipos y jugadores | Bajo | Ocasional | Eventual salvo identidad | Alta | Permanente |
| Usuarios | Alto potencial | Ocasional | Fuerte en identidad y rol | Alta | Vida de la cuenta |
| Sesiones | Alto y temporal | Muy frecuente | De sesión/fuerte local | Baja/media | TTL |
| Comentarios | Muy alto y variable | Masiva | Eventual, sesión y causal | Alta | A definir |
| Auditoría | Alto y continuo | Append-only | Causal por recurso | Crítica | Reciente + archivo |
| Multimedia | Alto en bytes | Ocasional | Eventual salvo derechos | Alta | Prolongada |
| API | Variable | Variable | Según recurso | No almacena | Según logs y trazas |

---

# 9. Dependencias y orden causal

Las siguientes relaciones deben respetarse aunque los datos terminen distribuidos:

1. Un equipo y jugador deben existir antes de ser referenciados en una convocatoria.
2. Un partido debe existir antes de recibir alineaciones o eventos.
3. Una alineación debe estar confirmada antes de validar participación.
4. Una sustitución requiere que el jugador saliente esté en cancha.
5. Un evento oficial confirmado puede modificar marcador, disciplina y rankings.
6. Los rankings dependen de eventos y estadísticas consolidadas.
7. El mapa de calor depende del intervalo real de participación.
8. Una corrección oficial debe regenerar las proyecciones afectadas.
9. La auditoría debe vincularse mediante request ID e identificador de operación.

Estas dependencias no implican necesariamente una transacción distribuida global. La estrategia de sincronización, idempotencia y reprocesamiento se definirá después de elegir responsabilidades.

---

# 10. Comportamiento general ante fallos

## 10.1 Principio de aislamiento

Una dependencia caída no debe inutilizar toda la plataforma.

Ejemplos:

- Si falla multimedia, fixture y estadísticas continúan.
- Si falla comentarios, se continúa consultando el partido.
- Si falla el almacenamiento de estadísticas, se muestra el último dato con timestamp.
- Si falla la fuente oficial de partidos, no se aceptan cambios oficiales, aunque pueda mostrarse una copia anterior.
- Si falla la sesión, las consultas públicas continúan y las operaciones protegidas se rechazan de manera segura.

## 10.2 No confirmar lo que puede perderse

Una operación oficial no debe responder éxito si quedó únicamente:

- En memoria.
- En una caché.
- En una cola no durable.
- En una proyección que no es la fuente oficial.

## 10.3 Recuperación

El diseño deberá permitir:

- Reintentos con backoff.
- Identificadores idempotentes.
- Reprocesamiento de mensajes.
- Reconstrucción de rankings y agregados.
- Reconstrucción de cachés.
- Detección de huecos.
- Reconciliación entre estado oficial y proyecciones.

---

# 11. Decisiones confirmadas en esta etapa

- Los motores todavía no se seleccionan en este documento.
- El patrón de acceso dominante será el primer criterio de selección.
- Los datos oficiales y los datos derivados tendrán requisitos diferentes.
- Fixture, alineaciones, sustituciones y eventos requieren alta consistencia y durabilidad.
- Las lecturas masivas de un partido no implican que existan escrituras oficiales masivas.
- Estadísticas y posiciones admiten consistencia eventual.
- Sesiones son temporales y separadas del perfil permanente.
- Comentarios requieren diseño específico para ráfagas y paginación temporal.
- Rankings y mapas agregados deben poder reconstruirse.
- La auditoría debe ser durable y distinta de los logs.
- Se utilizarán identificadores idempotentes en escrituras del proveedor.
- Las proyecciones no serán tratadas automáticamente como fuentes oficiales.
- Se documentará degradación por dependencia.
- La arquitectura objetivo se distinguirá de la prueba local.

---

# 12. Decisiones pendientes

- Concurrencia objetivo.
- Cantidad máxima de partidos simultáneos.
- Volumen esperado de comentarios por segundo.
- Cantidad de regiones o datacenters.
- Objetivo formal de disponibilidad.
- RPO y RTO por módulo.
- Retención definitiva de comentarios.
- Retención cruda y agregada de posiciones de jugadores.
- Política de eliminación de usuarios.
- Reglas deportivas de desempate de rankings.
- Alcance obligatorio de multimedia.
- Estrategia de sincronización entre fuente oficial y proyecciones.

---

# 13. Preguntas para el profesor

## Pregunta 1. Origen de los datos en vivo

> ¿Se espera una carga manual de estados, eventos, sustituciones y estadísticas, o podemos simular un proveedor externo que envíe automáticamente esa información a la API?

**Propuesta del grupo:** proveedor automático simulado y administrador solo para correcciones excepcionales.

## Pregunta 2. Escala obligatoria

> ¿El trabajo final debe utilizar una escala de tráfico, concurrencia, regiones y disponibilidad definida por la cátedra, o debemos proponer y justificar nuestros propios valores?

**Propuesta del grupo:** utilizar dos escenarios, prueba local demostrada y arquitectura objetivo basada en supuestos explícitos.

## Pregunta 3. Alcance de implementación

> ¿Todas las funcionalidades diseñadas deben quedar implementadas, o es válido implementar el núcleo y presentar algunas extensiones —como multimedia o archivo histórico— a nivel de arquitectura y prueba acotada?

**Propuesta del grupo:** implementar el núcleo y demostrar las extensiones más importantes con datos simulados, manteniendo multimedia como diseño conceptual.

---

# 14. Fundamento teórico utilizado

- **Clase 1:** volumen, velocidad, variedad, consistencia, ACID, BASE y relación entre requisitos y modelos de datos.
- **Clase 2:** fortalezas y límites de los modelos NoSQL; replicación, particionamiento, consistencia configurable y retención temporal.
- **Clase 3:** CAP, fallos de red, consistencia fuerte, eventual, de sesión y causal; replicación, clustering y particionado.
- **Clase 4:** modelo documental, documentos agregados, índices, replicación y sharding.
- **Clase 5:** grafos para navegación de relaciones y límites para flujos masivos simples.
- **Clase 6:** modelado por consulta, claves de partición y clustering, escrituras distribuidas y comentarios.
- **Clase 8:** datos temporales, sesiones, baja latencia, estructuras en memoria y cache-aside.

---

# 15. Próxima etapa

Con estos requisitos aprobados se podrá construir una matriz de decisión para cada funcionalidad comparando los seis modelos:

- MongoDB.
- Redis.
- Cassandra.
- InfluxDB.
- Neo4j.
- InterSystems IRIS fue evaluado en la comparación, pero quedó excluido de la arquitectura objetivo por decisión del grupo.

La comparación deberá incluir:

- Encaje del modelo.
- Patrón de acceso.
- Consistencia.
- Disponibilidad.
- Particionado y replicación.
- Rendimiento.
- Operación y recuperación.
- Ecosistema, profesionales y soporte.
- Complejidad de sincronización.
- Costo y dependencia tecnológica.

Solo después de esa comparación se definirá para cada necesidad:

- Fuente oficial.
- Capa de lectura caliente.
- Proyección especializada.
- Histórico.
- Mecanismo de sincronización.

---

## 16. Historial de cambios

### Versión 1.0 — 30 de octubre de 2026

- Creación del análisis de patrones de acceso.
- Separación entre prueba de concepto y arquitectura objetivo.
- Análisis de las quince áreas funcionales.
- Incorporación de consistencia, durabilidad, retención y fallos.
- Incorporación de fórmulas de volumen para estadísticas y mapas de calor.
- Registro de decisiones confirmadas y pendientes.
- Incorporación de preguntas para el profesor.

