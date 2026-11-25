$ErrorActionPreference = "Stop"
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$secretDir = Join-Path $projectRoot ".secretos"
$passwordPath = Join-Path $secretDir "neo4j-password.txt"
$authPath = Join-Path $secretDir "neo4j-auth.txt"

New-Item -ItemType Directory -Force -Path $secretDir | Out-Null

if (Test-Path $passwordPath) {
    $password = (Get-Content -Raw -Path $passwordPath).Trim()
} else {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $password = [Convert]::ToBase64String($bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
}

if ($password.Length -lt 16) { throw "No se pudo generar una contraseña segura para Neo4j." }
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($passwordPath, $password, $utf8NoBom)
[System.IO.File]::WriteAllText($authPath, "neo4j/$password", $utf8NoBom)

Write-Host "OK: secretos locales de Neo4j preparados y excluidos de Git/Docker build."
