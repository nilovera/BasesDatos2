# Evidencia reproducible

Esta carpeta conserva resultados del laboratorio vinculados a un commit. Los
archivos se generan con:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\capturar_evidencia.ps1 -Scenario verificacion-integrada
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_api.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_mongodb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_neo4j.ps1
```

Cada subcarpeta de ejecucion usa una marca temporal UTC. Antes de versionarla:

1. comprobar que no contiene secretos ni datos personales;
2. verificar que el commit registrado corresponde al codigo probado;
3. agregar capturas de Grafana con la misma ventana temporal si se usaran en la defensa;
4. documentar si cada valor fue medido, objetivo, estimado o no obtenido.

La captura integrada exige por defecto un árbol Git limpio y genera hashes de
los archivos. Los scripts nunca eliminan volúmenes: cada prueba detiene un solo
contenedor, comprueba la métrica y la alerta correspondiente, y lo recupera en
un bloque `finally`.
