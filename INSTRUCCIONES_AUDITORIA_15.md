# Incremento 15 — Auditoría y revisión documental

Actualización sobre la rama `trabajo-final`, base
`f4cb9be15f996d2710b41c36b18b09eed7e07da2`.

## Aplicación

1. Conservar un commit o una copia de los cambios locales del proyecto.
2. Extraer el ZIP sobre la raíz que contiene `docker-compose.yml`, reemplazando
   los archivos incluidos. Es una actualización de archivos, no una copia
   completa del repositorio.
3. Con Docker Desktop y la plataforma del incremento 14 disponibles, ejecutar:

```cmd
APLICAR_AUDITORIA_15.cmd
```

4. Ejecutar la comprobación funcional integrada:

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\probar_auditoria.ps1
```

El instalador crea los esquemas de auditoría y la cola de entrega y reconstruye
la API. Conserva simulaciones y volúmenes. La prueba publica un comentario
sintético, verifica replay, lo oculta y vuelve a mostrar, y prepara un cruce
nuevo sin iniciarlo. Guarda resultados sin el identificador de sesión.

## Contenido de la actualización

- Auditoría de publicación y moderación de comentarios.
- Registro y corrección de eventos oficiales.
- Auditoría de creación, inicio, pausa, reanudación y velocidad de simulaciones.
- Consultas por actor/día y recurso/día, con paginación estable.
- Entrega durable e idempotente desde MongoDB al historial Cassandra.
- Logs HTTP estructurados con correlación y duración, sin cuerpos ni secretos.
- Revisión formal de los Markdown de fundamentación, diseño, seguimiento,
  monitoreo y rendimiento, con estados respaldados por ejecuciones existentes.

El front conserva su alcance. Una solicitud sin sesión puede quedar como
anónima; los autores declarados se distinguen de sesiones de laboratorio y
servicios. Las identidades actuales no representan autenticación de producción.

## Consulta en Swagger

1. Abrir `http://localhost:8000/docs`.
2. Crear una sesión mediante `POST /api/v1/sesiones`, por ejemplo para
   `USR-0900`, rol `ADMIN` y TTL de 600 segundos.
3. Usar el `sesionId` devuelto en `X-Session-ID` para atribuir las operaciones
   correspondientes y consultar el historial.
4. Consultar `GET /api/v1/auditoria/actores/USR-0900` con `dia=YYYYMMDD` en UTC.
5. Consultar el comentario mediante
   `GET /api/v1/auditoria/recursos/COMENTARIO/{comentarioId}` y el mismo día.
6. Consultar `GET /api/v1/auditoria/pendientes` para observar entregas MongoDB
   que aún esperan confirmación Cassandra.

## Validación y documentación

El paquete incluye resultados de 170 pruebas unitarias y de regresión, con
25 específicas de auditoría. La comprobación HTTP real se ejecutó
correctamente el 27 de noviembre de 2026 con la API 0.10.0 y los motores del
laboratorio Docker. Su [resultado](evidencia/ejecuciones/auditoria-20261127T040527Z/resultado.json)
registra tres acciones del comentario, cero duplicados, rechazo de consulta
pública con 403 y envío MongoDB → Cassandra confirmado. El script se conserva
para reproducir la prueba; no es necesario reinstalar para incorporar este resultado.

La plataforma previa tiene registros Docker, fallas, carga y simulación. El
[estado de validación](docs/estado_validacion.md) vincula esos resultados con
sus commits. La [revisión documental](docs/revision_documental_15.md) explica
las correcciones de contenido y los controles aplicados. El
[diseño de auditoría](docs/diseno/10_auditoria_actividad.md) detalla su alcance.
