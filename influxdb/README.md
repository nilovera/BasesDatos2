# InfluxDB en Fixture2030

Este módulo integra InfluxDB 3 Core para posiciones, estadísticas y resúmenes
temporales. No contiene datos, tokens ni directorios internos de la base.

## Inicio

El comando general genera una credencial local si falta, crea las bases y
tablas de forma idempotente y levanta el resto de la plataforma:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
```

Los archivos `.secretos/influxdb-admin-token.json` y `.txt` están ignorados por
Git y por el contexto de build. No deben copiarse, mostrarse ni versionarse.

Antes del servidor, `influxdb-permissions` se ejecuta una sola vez como root,
ajusta el propietario del volumen nombrado al usuario interno `influxdb3` y
termina. No accede a la red, a los secretos ni a otras bases. Esto evita que un
volumen nuevo de Docker Desktop quede escribible solamente por root.

El token y el volumen forman una pareja operativa: se deben conservar juntos.
Si se pierde `.secretos/` pero permanece `fixture2030-influxdb-data`, no hay que
generar otra credencial ni borrar el volumen automáticamente; primero se debe
recuperar o rotar el token con un procedimiento explícito. El token offline solo
se adopta en la inicialización de un nodo que todavía no posee credenciales.

## Pruebas

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verificar_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_telemetria_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_plataforma.ps1
```

La prueba funcional carga cuatro posiciones con timestamps compartidos,
recorre un cursor estable, reconstruye un mapa de calor, genera 1.080 puntos de
equipo y produce 12 resúmenes históricos. Repetirla sobrescribe las mismas
identidades temporales y no aumenta el conteo esperado.

La prueba de persistencia reinicia solo `fixture2030-influxdb`. La prueba de
falla lo detiene temporalmente, exige estado degradado, `503` en telemetría,
continuidad del partido oficial, alerta `firing` y recuperación en `finally`.

No ejecutar `docker compose down -v`: eliminaría el volumen de laboratorio.
