# Backend — contrato inicial

El servicio todavía está pendiente de implementación, pero el contrato del
primer flujo vertical está disponible en `openapi.json`.

La API se reconstruirá de forma incremental. De la rama `monitoreo` se recuperarán únicamente adaptadores, diagnóstico y métricas que superen la revisión de dependencias, contratos y pruebas. Antes deben cerrarse el diseño físico de MongoDB y los contratos de escritura.

Primera aceptación: iniciar PAR-0001, registrar un gol, repetir el mismo evento sin duplicación, corregirlo, registrar una sustitución y consultar el resultado. La API no debe importar, configurar ni consultar IRIS. La outbox y la propagación a proyecciones requieren pruebas propias.

Este directorio no contiene todavía un servicio ejecutable.

## Contrato

- `GET /health`
- `GET /api/v1/partidos/{partidoId}`
- `GET /api/v1/partidos/{partidoId}/eventos`
- `POST /api/v1/partidos/{partidoId}/eventos`

Toda escritura requiere `Idempotency-Key`. El `201` representa una creación; el
`200` con `Idempotency-Replayed: true` representa una repetición válida; el
`409` informa conflicto de estado, versión o reutilización de clave con otro body.

