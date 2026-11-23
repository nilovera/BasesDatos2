# Backend — próximo incremento

Pendiente de implementación.

La API se reconstruirá de forma incremental. De la rama `monitoreo` se recuperarán únicamente adaptadores, diagnóstico y métricas que superen la revisión de dependencias, contratos y pruebas. Antes deben cerrarse el diseño físico de MongoDB y los contratos de escritura.

Primera aceptación: iniciar PAR-0001, registrar un gol, repetir el mismo evento sin duplicación y consultar el resultado. La API no debe importar, configurar ni consultar IRIS. La outbox y la propagación a proyecciones requieren pruebas propias.

Este directorio no contiene todavía un servicio ejecutable.

