@echo off
setlocal
cd /d "%~dp0"
if not exist "docker-compose.yml" (
  echo Extraer primero el paquete sobre la carpeta del proyecto Fixture2030.
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\aplicar_auditoria_15.ps1
if errorlevel 1 exit /b 1
echo Auditoria instalada. La comprobacion funcional se explica en INSTRUCCIONES_AUDITORIA_15.md.
exit /b 0
