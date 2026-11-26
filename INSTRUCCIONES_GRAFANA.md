# Actualización conjunta: partidos y distribución de Grafana

Este paquete incluye el incremento 13 de partidos y una nueva distribución del
tablero. Puede aplicarse directamente sobre el incremento 12 con su hotfix 01,
o sobre el incremento 13 si ya lo copiaste.

## Aplicar desde PowerShell

Descargar `Fixture2030_partidos_grafana.zip` en Descargas y ejecutar:

```powershell
$ErrorActionPreference = 'Stop'
$zip = Join-Path $env:USERPROFILE 'Downloads\Fixture2030_partidos_grafana.zip'
$tmp = Join-Path $env:TEMP ('Fixture2030_' + [guid]::NewGuid().ToString('N'))
$destino = 'C:\BasesDatos2-trabajo-final'
if (!(Test-Path -LiteralPath (Join-Path $destino 'docker-compose.yml'))) { throw 'No se encontro el proyecto de destino.' }
Expand-Archive -LiteralPath $zip -DestinationPath $tmp
Get-ChildItem -LiteralPath (Join-Path $tmp 'Fixture2030_actualizacion') -Force | Copy-Item -Destination $destino -Recurse -Force
Set-Location -LiteralPath $destino
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar la plataforma.' }
docker compose restart grafana
if ($LASTEXITCODE -ne 0) { throw 'No se pudo reiniciar Grafana.' }
```

Se copian los archivos del paquete respetando sus carpetas. Se reemplazan las
versiones correspondientes; los otros archivos del proyecto permanecen.
No se borran volúmenes, bases, secretos ni evidencia. La copia temporal de la
extracción no se elimina automáticamente.

## Nueva organización

1. Estado general: API y las seis bases en una sola fila compacta.
2. Rendimiento: latencia, errores HTTP y Outbox arriba; tráfico e historial
   de disponibilidad debajo.
3. Eventos oficiales y comentarios: eventos por tipo, actividad Cassandra
   y sus errores.
4. Redis: memoria, tasa de aciertos de caché y evictions.
5. Telemetría y relaciones: operaciones y errores de InfluxDB y Neo4j.
6. Data Mart: actividad analítica y errores.

Se conservan los 24 paneles de métricas, las consultas PromQL, el UID del
tablero, los umbrales, la fuente de datos, la ventana de 15 minutos y la
actualización cada cinco segundos. Se agregan seis encabezados de sección.
Las tarjetas de estado ocupan menos altura; los gráficos tienen leyendas
uniformes debajo y las ausencias de muestras se muestran como “Sin datos”.

Abrir el tablero existente en Grafana y recargar con Ctrl+F5. No hace falta
importar otro dashboard manualmente: el archivo conserva `uid=fixture2030-api`
y se sirve con el aprovisionamiento existente.

## Validación

JSON válido, IDs únicos, todos los paneles dentro de la grilla de 24 columnas,
sin superposiciones y todas las consultas originales preservadas exactamente.
La presentación final en Grafana debe comprobarse en el entorno Docker después
de copiar el paquete.
