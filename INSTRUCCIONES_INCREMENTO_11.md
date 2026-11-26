# Incremento 11 — simulador reproducible de partido

Este incremento agrega el motor backend de una transmisión simulada. Crea un
partido nuevo a partir de `PAR-0001`; no borra ni reinicia el partido base.

## Instalación

Desde `C:\BasesDatos2-trabajo-final`:

```cmd
xcopy "C:\Users\nicol\Downloads\trabajo-final-incremento-11-simulador\*" "." /E /H /K /Y
```

## Verificación previa

```cmd
python -m unittest discover -s tests -v
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_influxdb.ps1
```

## Prueba integral

```cmd
powershell -ExecutionPolicy Bypass -File scripts\probar_simulador_partido.ps1
```

La prueba usa semilla `2030` y velocidad `120x` para terminar en menos de dos
minutos. Comprueba pausa, reanudación, cambio de velocidad, eventos oficiales,
telemetría de jugadores y pelota, comentarios, marcador, relaciones del grafo
y convergencia de Outbox.

Para una demostración normal se recomienda `30x`: 90 minutos duran unos tres
minutos reales. Los controles también quedan disponibles en Swagger:

```text
http://localhost:8000/docs
```

No hacer commit hasta que la prueba integral finalice con `OK` y
`scripts\verificar_plataforma.ps1` confirme todos los componentes `UP`.

## Alcance

Este incremento implementa el simulador y sus contratos backend. El front de
espectador —cancha, reloj, línea de tiempo, comentarios y panel por base— se
incorpora en el incremento siguiente sobre estos endpoints.
