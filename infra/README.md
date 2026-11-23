# Infraestructura y observabilidad

El Compose actual levanta MongoDB, su inicializador, la API, Prometheus y
Grafana. Todos los puertos se publican solamente sobre `127.0.0.1`.

## Servicios actuales

| Servicio | Puerto local | Función |
|---|---:|---|
| API | 8000 | Contrato deportivo y `/metrics` |
| MongoDB | 27017 | Fuente oficial y Outbox |
| Prometheus | 9090 | Recolección de métricas técnicas |
| Grafana | 3000 | Dashboard `Fixture2030 — API y MongoDB` |

Grafana se aprovisiona automáticamente con Prometheus como fuente. Usuario
local: `admin`. La contraseña de laboratorio por defecto es `fixture2030` y
puede cambiarse definiendo `GRAFANA_ADMIN_PASSWORD` antes del primer arranque.
No es una configuración productiva.

Prometheus carga las reglas versionadas de `infra/prometheus/rules/`. Incluyen
indisponibilidad de la API, tasa de HTTP 5xx y acumulación de Outbox. Los
umbrales y responsables están documentados en
`docs/monitoreo/alertas_y_umbrales.md`.

## Ejecución

```powershell
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_flujo_mongodb.ps1
powershell -ExecutionPolicy Bypass -File scripts\capturar_evidencia.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_api.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_plataforma.ps1
```

Para detener sin borrar datos:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\detener_plataforma.ps1
```

No usar `docker compose down -v` salvo que se decida explícitamente eliminar
todos los volúmenes del laboratorio.

## Límites

El replica set MongoDB tiene un único miembro: permite transacciones, pero no
alta disponibilidad. Prometheus monitorea todavía la API y a sí mismo; los
exporters de los motores se agregarán con cada base. El dashboard actual es una
línea base, no evidencia aún un SLO alcanzado.
