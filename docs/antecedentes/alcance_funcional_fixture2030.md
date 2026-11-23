# Fixture 2030 — Alcance funcional

**Estado:** documento vivo  
**Versión:** 1.0  
**Fecha de actualización:** 24 de octubre de 2026  
**Objetivo:** consolidar el alcance funcional acordado para el trabajo final y registrar las decisiones pendientes de validación.

---

## 1. Alcance funcional de Fixture 2030

### 1.1 Contexto de la plataforma

Fixture 2030 será una plataforma backend para consultar y administrar información de una competencia internacional de fútbol.

Permitirá:

- Consultar equipos, jugadores, fixture y partidos.
- Seguir un partido en vivo.
- Registrar y consultar eventos oficiales.
- Consultar estadísticas temporales de equipos y jugadores.
- Generar mapas de calor de jugadores.
- Consultar rankings de rendimiento individual.
- Participar mediante comentarios.
- Mantener sesiones de usuarios.
- Auditar operaciones relevantes.
- Integrar todas las funcionalidades mediante una API REST.

El proyecto no busca construir una aplicación visual completa ni transmitir partidos. El producto principal será la arquitectura de datos políglota y su API.

La entrega deberá diferenciar claramente:

- La prueba de concepto implementada localmente.
- La arquitectura distribuida propuesta para un escenario productivo.
- Las funcionalidades completamente implementadas.
- Las funcionalidades diseñadas o simuladas.

### 1.2 Tipos de usuarios y actores

| Actor | Responsabilidad |
|---|---|
| Visitante | Consulta equipos, jugadores, partidos, eventos y estadísticas. |
| Usuario registrado | Mantiene su perfil y sesión, configura preferencias y publica comentarios. |
| Administrador | Mantiene catálogos, administra usuarios, modera comentarios, resuelve correcciones excepcionales y revisa la auditoría. |
| Proveedor de datos deportivos | Envía automáticamente estados, alineaciones, eventos y estadísticas del partido. |
| Sistema | Valida datos, actualiza resultados, genera agregados, expira información y actualiza proyecciones. |

No se implementará una gestión empresarial completa de identidades. Los roles se utilizarán para delimitar quién puede realizar cada operación.

No existirán roles separados de moderador ni de operador oficial:

- La moderación será responsabilidad del administrador.
- Los datos deportivos se recibirán mediante un proveedor automático simulado.
- El administrador solo intervendrá ante correcciones o situaciones excepcionales.

---

## 2. Catálogo funcional

### A. Equipos

#### Funcionalidades

- Consultar un equipo.
- Listar equipos.
- Filtrar por confederación.
- Consultar ranking.
- Consultar plantel convocado.
- Consultar cuerpo técnico.
- Actualizar información del catálogo.

#### Datos

- Código.
- Nombre.
- País representado.
- Confederación.
- Ranking.
- Escudo o URL del escudo.
- Director técnico.
- Plantel convocado.
- Fecha de actualización.

#### Alcance

Se administrará información descriptiva relativamente estable. No se incluirá la gestión contractual o económica de clubes y jugadores.

### B. Jugadores

#### Funcionalidades

- Consultar la ficha de un jugador.
- Buscar por equipo, nombre o posición.
- Consultar dorsal y club.
- Consultar estado de convocatoria.
- Relacionar al jugador con alineaciones, sustituciones, eventos y estadísticas.

#### Datos

- Código.
- Nombre completo.
- Fecha de nacimiento.
- Nacionalidad.
- Posición.
- Dorsal.
- Club.
- Selección.
- Estado de convocatoria.
- Pierna hábil, opcional.
- Fecha de actualización.

#### Alcance

La ficha no incluirá fotografía, contratos, salarios, representantes ni historiales médicos.

### C. Usuarios

#### Funcionalidades

- Crear un perfil.
- Consultar y actualizar el perfil.
- Seleccionar equipo favorito.
- Configurar idioma.
- Configurar preferencias y notificaciones.
- Asignar un rol.
- Relacionar al usuario con sesiones y comentarios.

#### Datos

- Código.
- Nombre visible.
- Correo.
- País.
- Idioma.
- Equipo favorito.
- Preferencias.
- Rol.
- Estado de la cuenta.
- Fecha de creación.

#### Alcance

Se incluirá el perfil funcional del usuario, pero quedarán fuera:

- Recuperación de contraseña.
- Inicio de sesión mediante Google o redes sociales.
- Autenticación multifactor.
- Gestión empresarial de identidad.
- Información de pago.

La autenticación podrá simularse para demostrar sesiones y roles.

### D. Fixture y partidos

#### Funcionalidades

- Consultar partidos por fecha.
- Consultar por fase, equipo o sede.
- Conocer participantes.
- Consultar marcador y estado.
- Programar o reprogramar un partido.
- Iniciar, suspender, reanudar y finalizar.
- Registrar tiempo adicional.
- Consultar árbitro y sede.
- Determinar cruces de fases eliminatorias.

#### Datos

- Código del partido.
- Competencia.
- Fase.
- Grupo o llave.
- Fecha y hora programada.
- Equipo local.
- Equipo visitante.
- Sede.
- Árbitro principal.
- Estado.
- Marcador.
- Hora real de inicio y finalización.
- Tiempo adicional.
- Partido anterior del que proviene cada clasificado, cuando corresponda.

#### Estados mínimos

```text
PROGRAMADO → EN_CURSO → FINALIZADO
                ↓
            SUSPENDIDO
                ↓
             REANUDADO
```

También deberá existir la posibilidad de cancelar o reprogramar un partido antes de su inicio.

#### Reglas principales

- Un partido no puede comenzar sin participantes.
- No puede finalizar antes de comenzar.
- No se aceptan eventos deportivos normales después de finalizar.
- Un partido suspendido no recibe eventos hasta ser reanudado.
- El marcador debe ser coherente con los goles oficiales.

### E. Alineaciones y sustituciones

Este módulo conecta jugadores, partidos, eventos y mapas de calor.

#### Funcionalidades

- Registrar titulares.
- Registrar suplentes.
- Asignar posición y dorsal.
- Confirmar la alineación.
- Registrar ingreso y salida de jugadores.
- Consultar quién estaba en cancha en un instante determinado.
- Calcular minutos jugados.

#### Datos de alineación

- Partido.
- Equipo.
- Jugador.
- Condición: titular o suplente.
- Posición.
- Dorsal.
- Estado.
- Fecha de confirmación.

#### Datos de sustitución

- Partido.
- Equipo.
- Jugador que sale.
- Jugador que entra.
- Minuto.
- Tiempo adicional.
- Timestamp real.
- Motivo opcional.

#### Regla fundamental

Una sustitución debe cerrar el intervalo de participación del jugador que sale y abrir el intervalo del jugador que entra. Esto permitirá generar correctamente los mapas de calor y los minutos jugados de titulares y suplentes.

### F. Eventos oficiales

#### Funcionalidades

- Registrar goles.
- Registrar tarjetas.
- Registrar faltas relevantes.
- Registrar penales.
- Registrar sustituciones.
- Consultar la secuencia cronológica.
- Asociar jugadores y equipos.
- Corregir o anular un evento oficial.
- Actualizar el marcador cuando corresponda.

#### Datos

- Identificador.
- Partido.
- Tipo.
- Período.
- Minuto.
- Tiempo adicional.
- Timestamp.
- Equipo.
- Jugador principal.
- Jugador relacionado.
- Detalle.
- Marcador posterior.
- Estado del evento.
- Proveedor o servicio de origen.

#### Correcciones

Un evento oficial no debe borrarse silenciosamente. Si se anula o corrige, deberán conservarse:

- El evento original.
- El motivo de la corrección.
- El administrador o servicio responsable.
- La fecha de la corrección.
- La nueva versión o evento compensatorio.

### G. Sesiones

#### Funcionalidades

- Crear sesión.
- Validar sesión.
- Renovar expiración.
- Registrar último acceso.
- Conservar el partido que está mirando el usuario.
- Cerrar sesión.
- Expirar automáticamente.

#### Datos

- Identificador de sesión.
- Usuario.
- Rol.
- Dispositivo.
- Fecha de creación.
- Último acceso.
- Partido actual.
- Estado.
- Cantidad de acciones.
- Tiempo restante de vida.

#### Alcance

La sesión no reemplaza el perfil permanente del usuario.

### H. Comentarios

#### Funcionalidades obligatorias

- Publicar comentarios.
- Consultar comentarios recientes por partido.
- Paginar cronológicamente.
- Consultar comentarios por usuario.
- Registrar likes.
- Ocultar o moderar contenido desde la administración.
- Mantener el estado de moderación.

#### Funcionalidades opcionales

- Responder comentarios.
- Mencionar usuarios.
- Denunciar contenido.

#### Datos

- Identificador.
- Partido.
- Usuario.
- Nombre visible.
- Contenido.
- Fecha.
- Likes.
- Estado de moderación.
- Comentario respondido, si corresponde.
- Menciones, si corresponde.

#### Alcance

No se construirá un sistema avanzado de moderación mediante inteligencia artificial. La moderación será administrativa o simulada.

### I. Estadísticas de equipos

#### Funcionalidades

- Consultar posesión.
- Consultar pases.
- Consultar tiros y tiros al arco.
- Consultar córners.
- Consultar faltas.
- Consultar recuperaciones.
- Comparar equipos.
- Ver la evolución durante el partido.
- Consultar datos detallados y resúmenes históricos.

#### Datos por medición

- Partido.
- Equipo.
- Timestamp.
- Posesión.
- Pases del intervalo.
- Pases acumulados.
- Tiros.
- Tiros al arco.
- Córners.
- Faltas.
- Recuperaciones.

#### Granularidad académica acordada

Para mantener congruencia con el Hito 8:

- Una medición cada 10 segundos.
- Precisión temporal en segundos.
- Resúmenes cada 15 minutos.
- Datos detallados con retención limitada.
- Resúmenes con mayor conservación.

No se documentará una captura por segundo ni resúmenes por minuto mientras los scripts trabajen con intervalos de 10 segundos y agregaciones de 15 minutos.

### J. Estadísticas de jugadores y mapas de calor

#### Estadísticas individuales

- Minutos jugados.
- Goles.
- Asistencias.
- Pases realizados.
- Pases completados.
- Tiros.
- Tiros al arco.
- Toques.
- Recuperaciones.
- Distancia recorrida.
- Velocidad máxima y promedio.
- Posiciones temporales.
- Mapa de calor.

#### Rankings de jugadores

- Máximo goleador.
- Máximo asistidor.
- Jugador con más pases completados.
- Jugador con más recuperaciones.
- Jugador con más tiros al arco.
- Jugador con mayor distancia recorrida, como ranking opcional.

#### Filtros para estadísticas y rankings

- Partido.
- Equipo.
- Grupo.
- Fase.
- Torneo completo.

#### Datos posicionales

- Partido.
- Jugador.
- Equipo.
- Timestamp.
- Período.
- Minuto y segundo.
- Posición X.
- Posición Y.
- Velocidad.
- Estado en cancha.
- Intervalo de participación.

#### Reglas

- Solo se consideran posiciones mientras el jugador está en cancha.
- El mapa del jugador sustituido finaliza al salir.
- El mapa del suplente comienza al ingresar.
- Los puntos pueden agruparse en celdas del campo para producir un mapa histórico.
- La entrada o salida se determina mediante la alineación y las sustituciones oficiales.
- Los goles y asistencias se obtienen de los eventos oficiales.
- Los pases y recuperaciones provienen de las estadísticas.
- Los minutos jugados se calculan utilizando alineaciones y sustituciones.
- La distancia recorrida se calcula a partir de las posiciones temporales.

#### Limitación

No habrá dispositivos GPS ni sensores reales. Los datos serán simulados, pero el modelo representará un flujo realista.

### K. Auditoría

#### Funcionalidades

- Registrar operaciones importantes.
- Saber quién o qué servicio realizó una modificación.
- Reconstruir cambios de estado.
- Registrar operaciones rechazadas.
- Vincular una operación con el `request_id` de la API.
- Investigar incidentes.
- Consultar auditoría por recurso, usuario, servicio o período.

#### Datos

- Identificador.
- Timestamp.
- Usuario o servicio.
- Acción.
- Recurso.
- Identificador del recurso.
- Estado anterior resumido.
- Estado posterior resumido.
- Resultado.
- Motivo del rechazo.
- Motor involucrado.
- Request ID.
- Dirección u origen.
- Fecha de expiración, si corresponde.

#### Operaciones que deben auditarse

- Cambios en el estado del partido.
- Alta, corrección o anulación de eventos.
- Confirmación de alineaciones.
- Sustituciones.
- Moderación administrativa de comentarios.
- Modificación de roles.
- Errores de autorización.
- Operaciones administrativas.

Los logs técnicos de la API seguirán existiendo, pero no reemplazan la auditoría de negocio.

### L. Multimedia

#### Funcionalidades incluidas

- Registrar metadatos de videos e imágenes.
- Asociar un recurso con un partido, evento o jugador.
- Consultar highlights.
- Recuperar una URL.
- Registrar formato, duración y derechos.
- Verificar integridad mediante checksum.

#### Datos

- Código.
- Tipo.
- Título.
- Partido.
- Evento.
- Jugador.
- Duración.
- Resolución.
- Formato.
- URL.
- Miniatura.
- Tamaño.
- Checksum.
- Derechos.
- Estado.
- Fecha de publicación.

#### Alcance

En la entrega final se implementarán, como máximo, los metadatos y las URLs simuladas. Quedan fuera:

- Subida de videos pesados.
- Transcodificación.
- Streaming.
- CDN real.
- Gestión comercial de derechos.
- Procesamiento automático de highlights.

El almacenamiento externo y la CDN se diseñarán arquitectónicamente, pero no será obligatorio desplegarlos.

### M. API REST integrada

#### Responsabilidades

- Exponer un contrato único.
- Validar datos.
- Identificar al usuario o servicio solicitante.
- Aplicar roles.
- Paginar resultados.
- Manejar errores uniformemente.
- Aplicar timeouts.
- Incluir `request_id`.
- Registrar auditoría.
- Degradar funcionalidades cuando una dependencia falla.
- Ocultar a los consumidores la distribución interna de los datos.

La API será la capa de acceso y coordinación, pero no será por sí misma una fuente de verdad.

---

## 3. Flujos principales

### 3.1 Antes del partido

1. Se consulta el fixture.
2. El proveedor envía participantes, sede y árbitro.
3. El proveedor envía la alineación confirmada.
4. El sistema identifica titulares y suplentes.
5. El sistema valida la información.
6. Se habilita automáticamente el seguimiento del partido.

### 3.2 Durante el partido

1. El proveedor informa el comienzo del partido.
2. El sistema modifica el estado a `EN_CURSO`.
3. El proveedor envía eventos oficiales.
4. El proveedor envía estadísticas de equipos y jugadores.
5. El proveedor envía posiciones de los jugadores.
6. El sistema valida y distribuye la información.
7. Los usuarios consultan el partido y publican comentarios.
8. Las operaciones relevantes se registran en auditoría.

No se asumirá que una persona carga manualmente cada pase, posición o evento.

### 3.3 Durante una sustitución

1. El proveedor informa la sustitución.
2. El sistema valida que ambos jugadores pertenezcan al equipo.
3. El sistema verifica que el jugador saliente esté en cancha.
4. Se cierra el intervalo de participación del jugador que sale.
5. Se abre el intervalo de participación del jugador que entra.
6. Se actualiza la alineación activa.
7. Los mapas de calor reflejan automáticamente el cambio.
8. La sustitución queda registrada como evento oficial.

### 3.4 Después del partido

1. El proveedor informa la finalización.
2. El sistema cambia el estado a `FINALIZADO`.
3. Se rechazan automáticamente nuevos eventos deportivos normales.
4. Se generan estadísticas agregadas.
5. Se calculan los rankings de jugadores.
6. Se conservan los datos históricos definidos.
7. Se compactan o eliminan los datos temporales según la política de retención.
8. La auditoría permite reconstruir las operaciones realizadas.

### 3.5 Correcciones excepcionales

Un administrador podrá intervenir para:

- Corregir un evento informado incorrectamente.
- Anular un gol.
- Resolver una alineación inconsistente.
- Corregir la identidad de un jugador.
- Reprocesar información enviada por el proveedor.

Una corrección no debe borrar silenciosamente el dato original: debe quedar registrada en auditoría.

---

## 4. Clasificación por prioridad

| Nivel | Funcionalidades |
|---|---|
| Núcleo obligatorio | Equipos, jugadores, fixture, partidos, alineaciones, eventos, sesiones, comentarios, estadísticas de equipos y API. |
| Ampliación importante | Usuarios, estadísticas de jugadores, rankings, mapas de calor, sustituciones completas y auditoría. |
| Diseño conceptual | Multimedia, almacenamiento externo y CDN. |
| Fuera de alcance | Frontend completo, streaming, sensores reales, pagos, venta de entradas, OAuth empresarial, IA de moderación y despliegue productivo real. |

Los mapas de calor, las sustituciones y la auditoría forman parte del alcance final, aunque su implementación pueda ser una prueba acotada. Estas funcionalidades permiten demostrar integración políglota, temporalidad, consistencia y trazabilidad.

---

## 5. Decisiones confirmadas en esta etapa

- El producto será una plataforma de datos y seguimiento del torneo.
- El entregable principal será el backend, la API y la arquitectura de datos.
- Habrá información previa, en vivo y posterior al partido.
- No existirán roles separados de moderador ni de operador oficial.
- Se modelará un proveedor externo de datos deportivos.
- La carga automática se simulará mediante scripts o solicitudes a la API.
- El administrador solo intervendrá en mantenimiento y correcciones excepcionales.
- Las alineaciones y sustituciones serán entidades explícitas.
- Los eventos oficiales admitirán correcciones auditadas.
- Los mapas de calor incluirán titulares, jugadores sustituidos y suplentes ingresados.
- Se incluirán rankings de goleadores, asistentes, pases y recuperaciones.
- La auditoría formará parte del diseño principal.
- Multimedia tendrá una implementación limitada a metadatos y URLs simuladas.
- No se prometerán sensores, streaming, frontend ni infraestructura productiva real.
- Los datos deportivos en vivo serán simulados.
- La documentación distinguirá implementación local y arquitectura objetivo.
- Las estadísticas mantendrán la congruencia del Hito 8: mediciones cada 10 segundos y resúmenes cada 15 minutos.

---

## 6. Preguntas para el profesor

### Pregunta 1. Origen de los datos en vivo

> Para el trabajo final, ¿se espera que el inicio, la finalización, los eventos, las sustituciones y las estadísticas del partido sean cargados manualmente por un operador, o podemos modelar un proveedor externo que los envíe automáticamente y simularlo mediante scripts o solicitudes a la API?

#### Propuesta del grupo

- Simular un proveedor oficial de datos deportivos.
- Enviar automáticamente eventos y estadísticas mediante la API.
- Mantener un administrador únicamente para correcciones excepcionales.
- Registrar todas las correcciones en auditoría.
- No depender de una carga manual continua durante el partido.

Esta alternativa resulta más coherente con una plataforma que debe administrar múltiples partidos y grandes cantidades de consultas.

#### Estado

**Pendiente de validación del profesor.**

---

## 7. Próxima etapa

Una vez validado este alcance, la siguiente etapa consistirá en definir para cada funcionalidad:

- Patrón de acceso dominante.
- Operaciones de lectura y escritura.
- Volumen esperado.
- Frecuencia de actualización.
- Latencia requerida.
- Consistencia necesaria.
- Retención.
- Comportamiento esperado ante fallos.

En esa etapa todavía no se elegirá la base de datos definitiva. Primero se establecerán los requisitos y luego se compararán los seis motores disponibles.

---

## 8. Historial de cambios

### Versión 1.0 — 24 de octubre de 2026

- Consolidación del alcance funcional inicial.
- Eliminación de los roles de moderador y operador oficial.
- Incorporación del proveedor automático de datos deportivos.
- Eliminación de colores de los datos de equipos.
- Eliminación de fotografía de los datos de jugadores.
- Incorporación de rankings de goleadores, asistentes, pases y recuperaciones.
- Revisión de los flujos antes, durante y después del partido.
- Incorporación de la sección de preguntas para el profesor.

