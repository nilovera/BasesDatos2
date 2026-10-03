# Hito 8 - Series temporales con InfluxDB 3 Core

## Descripcion

Este proyecto implementa el modulo de estadisticas temporales del Fixture 2030. Registra datos detallados de un partido, ejecuta consultas temporales, compara equipos, genera agregaciones y conserva resumenes historicos mediante InfluxDB 3 Core.

## Tecnologias

- Docker Desktop.
- WSL2 con Ubuntu.
- PowerShell.
- InfluxDB 3 Core.
- Line protocol.
- SQL para consultas temporales.

## Estructura

```text
fixture2030-influxdb/
|-- docker-compose.yml
|-- README.md
|-- scripts/
|   |-- inicializacion.ps1
|   |-- creacion_modelo.ps1
|   |-- generar_datos.ps1
|   |-- cargar_datos.ps1
|   |-- consultas.ps1
|   |-- agregacion.ps1
|   `-- validacion.ps1
`-- docs/
    |-- patrones_de_acceso.md
    |-- modelo_multidimensional.md
    |-- cardinalidad_y_escalabilidad.md
    |-- retencion_y_granularidad.md
    |-- resultados_pruebas.md
    `-- evidencia/
```

La carpeta `datos` se genera localmente y no se versiona.

## 1. Preparar persistencia

Desde PowerShell:

```powershell
wsl -d Ubuntu -- bash -lc 'mkdir -p ~/docker/data/influxdb && chmod -R 777 ~/docker/data/influxdb'
```

## 2. Iniciar el ambiente

```powershell
cd C:\fixture2030-influxdb

wsl -d Ubuntu -- bash -lc 'cd /mnt/c/fixture2030-influxdb && docker compose up -d'

Start-Sleep -Seconds 15

wsl -d Ubuntu -- bash -lc 'cd /mnt/c/fixture2030-influxdb && docker compose ps'
```

## 3. Crear el token local

Este paso se realiza una sola vez en un ambiente nuevo:

```powershell
$tokenData = docker exec fixture2030-influxdb `
    influxdb3 create token --admin --format json |
    ConvertFrom-Json

$tokenData.token | Set-Content -NoNewline ".\.influxdb3-token"

Remove-Variable tokenData
```

No se debe mostrar, capturar ni subir el token. El archivo `.influxdb3-token` esta excluido mediante `.gitignore`.

## 4. Habilitar scripts para la terminal actual

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

Este cambio dura unicamente mientras permanezca abierta la terminal.

## 5. Verificar el ambiente

```powershell
& ".\scripts\inicializacion.ps1"
```

## 6. Crear las bases y tablas

Solo debe ejecutarse en la primera inicializacion:

```powershell
& ".\scripts\creacion_modelo.ps1"
```

Se crean:

- `fixture2030_detalle`, con retencion de 7 dias.
- `fixture2030_historico`, con retencion de 365 dias.
- `estadisticas_equipo`.
- `resumen_equipo_minuto`.

## 7. Generar los datos

```powershell
& ".\scripts\generar_datos.ps1"
```

El generador produce 1.080 puntos: dos equipos, 540 puntos por equipo, una muestra cada 10 segundos, 90 minutos de partido y precision temporal en segundos.

## 8. Cargar los puntos

```powershell
& ".\scripts\cargar_datos.ps1"
```

La carga utiliza cinco lotes con un maximo de 250 puntos por lote.

## 9. Ejecutar consultas

```powershell
& ".\scripts\consultas.ps1"
```

Incluye una ventana temporal, filtros por partido y equipo, comparacion entre Argentina y Mexico y agregacion cada 15 minutos.

## 10. Crear el resumen historico

```powershell
& ".\scripts\agregacion.ps1"
```

El proceso reduce 1.080 puntos detallados a 12 resumenes historicos.

## 11. Validar resultados

```powershell
& ".\scripts\validacion.ps1"
```

Resultado esperado: 1.080 puntos detallados, 540 puntos por equipo, dos equipos y 12 resumenes historicos.

## 12. Verificar persistencia

```powershell
wsl -d Ubuntu -- bash -lc 'cd /mnt/c/fixture2030-influxdb && docker compose restart influxdb'

Start-Sleep -Seconds 15

& ".\scripts\validacion.ps1"
```

## 13. Detener el ambiente

```powershell
wsl -d Ubuntu -- bash -lc 'cd /mnt/c/fixture2030-influxdb && docker compose down'
```

Los datos permanecen en `~/docker/data/influxdb`.

## Modelo temporal

### Tags

- `partido_id`.
- `equipo_id`.

Son dimensiones utilizadas para localizar y comparar series.

### Fields

- `posesion_pct`.
- `pases_intervalo`.
- `tiros_acumulados`.

Son valores observados y no se utilizan como tags para evitar cardinalidad innecesaria.

### Tiempo

Los puntos usan timestamps Unix con precision en segundos.

## Seguridad

- El token se almacena fuera de los scripts.
- `.influxdb3-token` no debe versionarse.
- No se incluyen credenciales en capturas.
- La carpeta persistente queda fuera del repositorio.
- El puerto se publica unicamente en `127.0.0.1:8181`.

## Evidencias

Las capturas se encuentran en `docs/evidencia`. Los resultados y las limitaciones de la prueba local estan documentados en `docs/resultados_pruebas.md`.
