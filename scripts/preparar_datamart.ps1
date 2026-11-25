$ErrorActionPreference = "Stop"
$secretDir = Join-Path (Split-Path $PSScriptRoot -Parent) ".secretos"
$passwordPath = Join-Path $secretDir "datamart-password.txt"

New-Item -ItemType Directory -Force -Path $secretDir | Out-Null
if (-not (Test-Path $passwordPath)) {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $password = [Convert]::ToBase64String($bytes).Replace("/", "_").Replace("+", "-")
    [System.IO.File]::WriteAllText($passwordPath, $password, (New-Object System.Text.UTF8Encoding($false)))
}
Write-Host "OK: secreto local del Data Mart preparado y excluido de Git."
