ECHO "=== HITO 8 - INICIALIZACION DEL AMBIENTE INFLUXDB ==="
Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"

ECHO "1. Verificacion de disponibilidad"
docker compose ps

ECHO "2. Verificacion de version"
docker exec fixture2030-influxdb influxdb3 --version

ECHO "3. Verificacion de imagen utilizada"
docker inspect fixture2030-influxdb --format '{{.Config.Image}}'

ECHO "4. Verificacion de montajes de datos y scripts"
docker inspect fixture2030-influxdb --format '{{range .Mounts}}{{println .Source .Destination .RW}}{{end}}'

ECHO "5. Verificacion del puerto publicado"
docker port fixture2030-influxdb 8181

ECHO "6. Inspeccion de permisos de datos y scripts"
docker exec fixture2030-influxdb /bin/sh -c 'ls -ld /var/lib/influxdb3/data /scripts'

ECHO "=== INICIALIZACION FINALIZADA ==="
