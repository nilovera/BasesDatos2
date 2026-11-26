@echo off
setlocal
cd /d "%~dp0"
if not exist "docker-compose.yml" (
    echo No se encontro docker-compose.yml. Copiar primero el contenido del paquete al proyecto.
    exit /b 1
)
echo Actualizando plataforma...
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
if errorlevel 1 exit /b 1
echo Limpiando una sola vez las simulaciones anteriores con respaldo...
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\limpiar_simulaciones.ps1 -Aplicar
if errorlevel 1 exit /b 1
docker compose restart grafana
if errorlevel 1 exit /b 1
echo Actualizacion completada. Recargar el front y Grafana con Ctrl+F5.
exit /b 0
