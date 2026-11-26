# Cambios 14 — Reloj, historial y monitoreo

Incluye la navegación de partidos del incremento 13. Reemplaza la distribución
de Grafana de la actualización anterior.

## Aplicar desde CMD

Descargar `Fixture2030_cambios_14.zip` en Descargas. Ejecutar cada comando en
orden; si aparece un error, no continuar con el siguiente:

```cmd
powershell -NoProfile -Command "Expand-Archive -LiteralPath '%USERPROFILE%\Downloads\Fixture2030_cambios_14.zip' -DestinationPath '%TEMP%\fixture2030-cambios14' -Force"
xcopy "%TEMP%\fixture2030-cambios14\Fixture2030_actualizacion14\*" "C:\BasesDatos2-trabajo-final\" /E /I /Y
cd /d C:\BasesDatos2-trabajo-final
APLICAR_CAMBIOS_14.cmd
```

El último comando reconstruye la plataforma, aplica una única limpieza del
historial con respaldo y reinicia Grafana. Luego recargar ambas pantallas
con Ctrl+F5. No elimina volúmenes ni reinicia los contadores de IDs.

## Marcador

El reloj principal muestra `23 min`, sin segundos. El reloj lógico del motor
sigue avanzando por segundos para mantener la coherencia de los eventos y
la telemetría. Si una URL apunta a una simulación retirada, se limpia la vista
y se vuelve a buscar el partido activo sin mezclar datos del anterior.

## Limpieza del historial

Se retiran de la colección activa `simulaciones` todas las simulaciones
anteriores en estado `LISTA`, `FINALIZADA` o `ERROR`. Se conservan las que están
`EJECUTANDO` o `PAUSADA`, y se relee el estado dentro de cada transacción para
proteger una simulación que se inicia durante el procedimiento.

Antes de retirar cada documento, se guarda completo en
`fixture2030.simulaciones_archivadas`, asociado a un lote `LIM-...`. El respaldo
y la eliminación son parte de la misma transacción. Si el respaldo falla,
esa simulación no se elimina. Un fallo posterior permite recuperar las que
ya se hayan respaldado.

Esta limpieza vacía el historial de simulaciones de la pantalla. **Los partidos
oficiales, eventos, relaciones, comentarios y series históricas de las bases
se conservan como evidencia**; no es un borrado físico completo de esos datos.
El catálogo de equipos y jugadores y el partido base permanecen disponibles.

La marca `mantenimientos/limpieza-incremento-14` impide que volver a aplicar
esta actualización borre los partidos nuevos. Si la limpieza se interrumpe,
el reintento conserva el mismo corte y lote de respaldo.

Para ver los candidatos sin limpiar:

```cmd
powershell -ExecutionPolicy Bypass -File scripts\limpiar_simulaciones.ps1
```

Para recuperar un lote, reemplazar `LIM-...` por el ID completo impreso durante
la limpieza:

```cmd
powershell -ExecutionPolicy Bypass -File scripts\limpiar_simulaciones.ps1 -RestaurarLote LIM-...
```

La recuperación no pisa documentos existentes ni inicia partidos.

## Grafana

Se eliminan los paneles de Outbox, Operaciones Neo4j y la sección y tarjetas
de Data Mart. Los procesos de integración y analítica siguen funcionando.

La nueva distribución contiene:

- Disponibilidad de API, MongoDB, Redis, Cassandra, InfluxDB y Neo4j.
- Latencias HTTP p50, p95 y p99, calculadas sobre endpoints `/api/v1/` en
  ventanas de cinco minutos.
- Throughput total y por endpoint, en solicitudes completadas por segundo.
- Concurrencia actual y evolución temporal: solicitudes `/api/` simultáneamente
  en proceso en esta instancia de API. No equivale a usuarios conectados.
- Errores HTTP 5xx de los últimos cinco minutos.
- MongoDB: conexiones abiertas, tamaño lógico, almacenamiento asignado,
  tamaño de índices y operaciones por segundo.
- Memoria, aciertos de caché y evictions de Redis.
- Eventos, actividad de comentarios y telemetría, y errores por motor.

Las métricas de MongoDB provienen de `serverStatus` y `dbStats` mediante un
collector del endpoint `/metrics`. No se exportan documentos ni secretos. Una
falla de lectura publica `fixture2030_mongodb_metrics_up=0` y no inventa valores
cero para las métricas ausentes. Referencia técnica:
https://www.mongodb.com/docs/manual/reference/command/serverstatus/

Las mediciones HTTP excluyen sondas de salud, archivos estáticos y scrapes del
tablero. Sin tráfico pueden faltar percentiles o tasas. Las consultas usan
las muestras disponibles; la ventana completa de cinco minutos se reúne
después del arranque. Prometheus muestrea cada cinco segundos y puede no captar
picos de concurrencia más breves.

## Validación del paquete

Las pruebas cubren respaldo antes de eliminar, fallo del respaldo, cambio de
estado concurrente, restauración idempotente, reaplicación sin borrar partidos
nuevos, registro de concurrencia y cancelación, y métricas MongoDB sin muestras
falsas cuando falla la lectura. Se verifica también la sintaxis del front y
la grilla de Grafana sin paneles superpuestos.

La limpieza real y la comprobación integral de métricas se ejecutan en tu
Docker al aplicar el paquete; no se presentan resultados de contenedores que
no se pudieron ejecutar desde este entorno.
