$ErrorActionPreference = "Stop"

Set-Location "C:\fixture2030-api"

$python = ".\.venv\Scripts\python.exe"
$redisKey = "sesion:SES-PERF-0001"

$processor = Get-CimInstance Win32_Processor |
    Select-Object -First 1

$computer = Get-CimInstance Win32_ComputerSystem

$env:HITO10_CPU_NAME = $processor.Name
$env:HITO10_CPU_CORES = (
    $processor.NumberOfCores.ToString()
)
$env:HITO10_CPU_LOGICAL = (
    $processor.NumberOfLogicalProcessors.ToString()
)
$env:HITO10_RAM_GB = (
    [math]::Round(
        $computer.TotalPhysicalMemory / 1GB,
        2
    )
).ToString(
    [System.Globalization.CultureInfo]::InvariantCulture
)

try {
    Write-Host "=== VERIFICAR API ==="

    Invoke-WebRequest `
        -Uri "http://127.0.0.1:8000/health" `
        -UseBasicParsing |
        Out-Null

    Write-Host "API disponible."

    Write-Host "`n=== PREPARAR SESION REDIS ==="

    $lastAccess = (
        Get-Date
    ).ToUniversalTime().ToString(
        "yyyy-MM-ddTHH:mm:ssZ"
    )

    docker exec fixture2030-redis `
        redis-cli DEL $redisKey |
        Out-Null

    docker exec fixture2030-redis `
        redis-cli HSET `
        $redisKey `
        sesion_id "SES-PERF-0001" `
        usuario_id "USR-PERF" `
        rol "fan" `
        ultimo_acceso $lastAccess `
        estado "activa" `
        partido_actual "PAR-0001" `
        acciones "1" |
        Out-Null

    docker exec fixture2030-redis `
        redis-cli EXPIRE $redisKey 900 |
        Out-Null

    Write-Host "Sesion preparada."

    Write-Host "`n=== EJECUTAR MEDICION ==="

    & $python -m scripts.medir_rendimiento

    if ($LASTEXITCODE -ne 0) {
        throw "La medicion registro fallos."
    }
}
finally {
    docker exec fixture2030-redis `
        redis-cli DEL $redisKey `
        2>$null |
        Out-Null

    Remove-Item `
        Env:HITO10_CPU_NAME, `
        Env:HITO10_CPU_CORES, `
        Env:HITO10_CPU_LOGICAL, `
        Env:HITO10_RAM_GB `
        -ErrorAction SilentlyContinue
}
