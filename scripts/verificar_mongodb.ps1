$ErrorActionPreference = "Stop"

Write-Host "Verificando replica set, catalogo e indices..."
docker compose exec -T mongo mongosh --quiet `
  "mongodb://localhost:27017/?directConnection=true" `
  /opt/fixture2030/init/03_verify.js
if ($LASTEXITCODE -ne 0) {
    throw "La verificacion de MongoDB fallo (codigo $LASTEXITCODE)."
}
