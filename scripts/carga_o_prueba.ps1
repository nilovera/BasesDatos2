param(
    [ValidateRange(1, 2000000)]
    [int]$Cantidad = 1000128
)

$ErrorActionPreference = "Stop"

# Las rutas se calculan desde la ubicación del propio script.
$rutaProyecto = Split-Path -Parent $PSScriptRoot
$rutaDatos = Join-Path $rutaProyecto "data"
$rutaPartido = Join-Path $rutaDatos "comentarios_por_partido.csv"
$rutaUsuario = Join-Path $rutaDatos "comentarios_por_usuario.csv"

New-Item -ItemType Directory -Path $rutaDatos -Force | Out-Null

$nombres = @(
    "Ana", "Bruno", "Carla", "Diego", "Elena",
    "Francisco", "Gabriela", "Hugo", "Inés", "Javier",
    "Lucía", "Martín", "Natalia", "Oscar", "Paula",
    "Ramiro", "Sofía", "Tomás", "Valentina", "Walter"
)

$apellidos = @(
    "Torres", "Silva", "Méndez", "Rossi", "García",
    "Costa", "Pereira", "Fernández", "Martínez", "Romero",
    "Navarro", "López", "Sánchez", "Alvarez", "Morales",
    "Castro", "Vega", "Suárez", "Herrera", "Benítez"
)

$utf8SinBom = [System.Text.UTF8Encoding]::new($false)
$escritorPartido = [System.IO.StreamWriter]::new($rutaPartido, $false, $utf8SinBom, 1048576)
$escritorUsuario = [System.IO.StreamWriter]::new($rutaUsuario, $false, $utf8SinBom, 1048576)

$inicio = Get-Date
$fechaBase = [datetime]"2030-06-13 18:00:00"

try {
    $escritorPartido.WriteLine("partido_id,bucket_10min,creado_en,comentario_id,usuario_id,usuario_nombre,contenido,estado_moderacion,likes")
    $escritorUsuario.WriteLine("usuario_id,bucket_dia,creado_en,comentario_id,partido_id,usuario_nombre,contenido,estado_moderacion,likes")

    for ($i = 0; $i -lt $Cantidad; $i++) {
        # Distribución uniforme entre los 96 partidos del Hito 5.
        $numeroPartido = ($i % 96) + 1
        $partidoId = "PAR-{0:D4}" -f $numeroPartido

        # Cada partido posee una ventana de actividad de 120 minutos.
        $secuenciaPartido = [math]::Floor($i / 96)
        $segundoPartido = $secuenciaPartido % 7200
        $desplazamientoDia = [math]::Floor(($numeroPartido - 1) / 8)
        $creadoEn = $fechaBase.AddDays($desplazamientoDia).AddSeconds($segundoPartido)
        $creadoTexto = $creadoEn.ToString("yyyy-MM-dd HH:mm:ss.fff+0000", [System.Globalization.CultureInfo]::InvariantCulture)

        $minutoBucket = [int]([math]::Floor($creadoEn.Minute / 10) * 10)
        $bucket10min = $creadoEn.ToString("yyyyMMddHH") + ("{0:D2}" -f $minutoBucket)
        $bucketDia = $creadoEn.ToString("yyyyMMdd")

        # UUID determinista: repetir el script produce las mismas claves.
        $comentarioId = "33333333-3333-3333-3333-{0:x12}" -f ($i + 1)

        $numeroUsuario = ($i % 50000) + 1
        $usuarioId = "USR-{0:D6}" -f $numeroUsuario
        $indiceNombre = [int](($numeroUsuario - 1) % $nombres.Count)
        $indiceApellido = [int]([math]::Floor(($numeroUsuario - 1) / $nombres.Count) % $apellidos.Count)
        $usuarioNombre = $nombres[$indiceNombre] + " " + $apellidos[$indiceApellido]

        if (($i % 20) -eq 0) {
            $estado = "oculto"
        }
        elseif (($i % 10) -eq 0) {
            $estado = "pendiente"
        }
        else {
            $estado = "visible"
        }

        $likes = $i % 101
        $contenido = "Comentario $($i + 1) del partido $partidoId"

        $escritorPartido.WriteLine("$partidoId,$bucket10min,$creadoTexto,$comentarioId,$usuarioId,$usuarioNombre,$contenido,$estado,$likes")
        $escritorUsuario.WriteLine("$usuarioId,$bucketDia,$creadoTexto,$comentarioId,$partidoId,$usuarioNombre,$contenido,$estado,$likes")

        if ((($i + 1) % 100000) -eq 0) {
            Write-Host "$($i + 1) comentarios generados..."
        }
    }
}
finally {
    $escritorPartido.Close()
    $escritorUsuario.Close()
}

$duracion = (Get-Date) - $inicio
$tamanoPartidoMb = [math]::Round((Get-Item $rutaPartido).Length / 1MB, 2)
$tamanoUsuarioMb = [math]::Round((Get-Item $rutaUsuario).Length / 1MB, 2)

Write-Host "Generación reproducible finalizada."
Write-Host "Comentarios únicos generados: $Cantidad"
Write-Host "Filas físicas preparadas: $($Cantidad * 2)"
Write-Host "Partidos utilizados: 96"
Write-Host "Usuarios posibles: 50000"
Write-Host "Archivo por partido: $tamanoPartidoMb MB"
Write-Host "Archivo por usuario: $tamanoUsuarioMb MB"
Write-Host "Tiempo de generación: $([math]::Round($duracion.TotalSeconds, 2)) segundos"

