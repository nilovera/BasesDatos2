# Incremento 12 — Transmisión web del partido

Aplicar sobre la rama `trabajo-final` que contiene `e51b652`. El paquete contiene únicamente archivos nuevos o modificados por este incremento.

## Instalar y verificar

Desde `C:\BasesDatos2-trabajo-final`, después de copiar el contenido del paquete:

```cmd
python -m unittest discover -s tests -v
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_frontend.ps1
start "" "http://127.0.0.1:8000/directo"
```

La pantalla se sirve en el contenedor de la API y utiliza el mismo puerto 8000; no requiere Node ni instalar dependencias de front. Abrirla consulta el último partido y no crea uno nuevo. `?simulacion=SIM-...` permite fijar un partido concreto. Las recargas conservan ese partido si la URL tiene el parámetro.

## Lanzar una demo nueva

```cmd
powershell -ExecutionPolicy Bypass -File scripts\iniciar_demo_partido.ps1 -Semilla 2030 -Velocidad 25
```

El comando crea un partido, lo inicia y abre la transmisión. 25× equivale nominalmente a 3 minutos 36 segundos para 90 minutos lógicos. Las escrituras y recursos de la máquina pueden aumentar la duración real. No ejecutar varias demos simultáneas: el worker procesa una simulación por vez. El script de prueba integral del incremento 11 sigue disponible para comprobar pausa y reanudación.

La pantalla incluye marcador y reloj, velocidad, eventos con autor y asistencia, comentarios, posiciones de jugadores/pelota y mapa de calor por jugador o equipo. Los goles se marcan en sus coordenadas; el VAR se muestra en la línea de tiempo y no suma al marcador. No contiene controles de inicio/pausa, estados técnicos de bases ni enlaces de monitoreo.

## Comprobar visualmente

1. Abrir la última demo y comprobar que reloj y marcador avanzan.
2. Cambiar la velocidad durante el partido y esperar la próxima actualización.
3. Alternar posiciones y mapa de calor; seleccionar un jugador y después su equipo.
4. Esperar un gol y verificar autor, asistencia, estrella en cancha y marcador.
5. Esperar el VAR y comprobar que no suma goles.
6. Al finalizar, recargar la misma URL: deben conservarse marcador, eventos, telemetría y comentarios finales.

Los comentarios se consultan en tres buckets de minuto UTC; al finalizar se toma la hora final, para poder volver a verlos días después. El mapa acumula todas las posiciones del partido en una grilla 20×12. La cancha muestra la última muestra de InfluxDB y el reloj el último progreso confirmado por el worker. Puede existir una diferencia breve entre ambos; la hora de la muestra está visible. Los números dentro de los puntos corresponden al sufijo del ID de jugador, no a dorsales oficiales. Las posiciones de catálogo son generales (defensor, mediocampista, delantero y arquero).

## Documento de comprobación

`docs/demo/consultas_comprobacion_partido.md` contiene las consultas directas por base y qué observar. Los resultados en crudo se obtienen al ejecutar las consultas; el documento no inventa respuestas ni horas de ejecución.

## Evidencia y versionado

Revisar `git status --short` y los cambios antes de agregar archivos. El comando `verificar_frontend.ps1` genera `evidencia/ejecuciones/frontend-.../resultado.json`, que valida lecturas y recursos HTTP, no la presentación visual. Para evidencia asociada a código limpio, versionar el incremento antes de volver a ejecutar ese chequeo y guardar la evidencia en un segundo commit.
