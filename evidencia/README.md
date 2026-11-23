# Evidencia reproducible

Esta carpeta conserva resultados del laboratorio vinculados a un commit. Los
archivos se generan con:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\capturar_evidencia.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_api.ps1
```

Cada subcarpeta de ejecucion usa una marca temporal UTC. Antes de versionarla:

1. comprobar que no contiene secretos ni datos personales;
2. verificar que el commit registrado corresponde al codigo probado;
3. agregar capturas de Grafana con la misma ventana temporal si se usaran en la defensa;
4. documentar si cada valor fue medido, objetivo, estimado o no obtenido.

Los scripts nunca eliminan volumenes. La prueba de falla detiene solamente la
API, comprueba `up=0` y la alerta `Fixture2030ApiDown` en estado `firing`, y la
recupera en un bloque `finally`.
