# Capturas redactadas

Guardar aquí solo capturas en las que **no** se vean passwords, tokens, URI con
credenciales, archivos `.env` ni datos personales (RNF7, RNF8).

Antes de agregar una captura:

1. Verificar que la terminal no muestre el contenido de `.env` ni comandos con `--password`.
2. Tapar con un rectángulo sólido cualquier secreto (no usar desenfoque).
3. Mantener visibles fecha/hora, comando, host:puerto, estado y request ID, que son
   necesarios para interpretar el diagnóstico.

Nombres sugeridos:

| Archivo | Contenido |
|---|---|
| `01_docker_ps.png` | `docker ps` con nombres, estado y puertos publicados |
| `02_modo_tcp.png` | salida de `evaluar_conectividad.ps1 -Modo tcp` |
| `03_modo_nativos.png` | salida de `-Modo nativos` (resumen por producto) |
| `04_modo_api.png` | salida de `-Modo api` con request IDs y logs asociados |
| `05_health_dependencias.png` | `GET /health/dependencias` en Swagger o navegador |
| `06_falla_durante.png` | API respondiendo 503 con el contenedor detenido |
| `07_falla_recuperada.png` | misma ruta respondiendo 200 después de `docker start` |
| `08_matriz.png` | `docs/matriz_de_conectividad.md` renderizada en GitHub |
