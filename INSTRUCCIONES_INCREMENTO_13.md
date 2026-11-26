# Incremento 13 — Elegir y jugar el siguiente partido

Aplicar sobre la rama `trabajo-final` con el incremento 12 y su hotfix 01.
El ZIP contiene solo archivos nuevos o modificados. Copiar su contenido sobre
`C:\BasesDatos2-trabajo-final`, conservando las carpetas del paquete.

## Actualizar

Desde CMD, en `C:\BasesDatos2-trabajo-final`:

```cmd
python -m unittest discover -s tests -v
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_partidos.ps1
start "" "http://127.0.0.1:8000/directo"
```

Recargar la página con Ctrl+F5 si estaba abierta. No se borran volúmenes ni
partidos anteriores. No hace falta instalar Node para usar la pantalla.

## Pasar a otro partido

1. Abrir **Agregar un partido a los próximos cruces**.
2. Elegir local y visitante, y pulsar **Agregar a próximos**.
3. Repetir para dejar preparados los partidos que siguen.
4. Pulsar **Jugar y ver** en un cruce, o **Jugar siguiente partido** para el
   primero que se agregó. Se abre su transmisión con un ID fijo en la URL.
5. Los cruces pendientes permanecen en **Por jugar**. En **En curso** se abre
   el partido que está ejecutándose. En **Finalizados** se consultan los resultados.

Cambiar de transmisión no detiene el partido que está corriendo. El laboratorio
admite un partido ejecutándose por vez: al terminar, se habilita el siguiente.
Si quedó pausado o interrumpido, aparece **Continuar y ver** en En curso.
La lista se actualiza cada cinco segundos, tiene paginación y permite volver
a abrir los partidos anteriores con sus datos.

## Qué significa “próximos”

Son las simulaciones guardadas en MongoDB en estado `LISTA`, ordenadas por
creación. No se genera un torneo oficial ni una llave eliminatoria. Si aún no
preparaste cruces, la lista muestra cómo agregarlos. Los 64 equipos provienen
del catálogo existente; el partido base `PAR-0001` sigue siendo una plantilla
y no se mezcla con los partidos efectivamente preparados para jugar.

El partido nuevo guarda los equipos elegidos y las alineaciones correspondientes.
El flujo de goles, comentarios y telemetría sigue usando el simulador existente.
Las consultas de evidencia continúan fuera del front.

## Cambios técnicos

- `GET /api/v1/directo/partidos?grupo=proximos|en-curso|finalizados&pagina=0`.
- `GET /api/v1/directo/equipos`.
- `POST /api/v1/simulaciones` acepta opcionalmente `localId` y `visitanteId`;
  deben existir y ser distintos. Las llamadas antiguas siguen usando el partido base.
- El inicio usa un índice único parcial `uq_simulacion_ejecutando` en MongoDB.
  Evita dos inicios simultáneos incluso desde pestañas distintas. Se crea al
  intentar iniciar o continuar, sin migración manual. Si un entorno anterior
  ya tiene varios documentos `EJECUTANDO`, devuelve conflicto y requiere revisar
  esas ejecuciones antes de iniciar otra; no se cambian automáticamente.
- Los listados usan proyecciones explícitas: no exponen el plan futuro de eventos.

## Validación realizada al preparar el paquete

- 134 pruebas de Python aprobadas.
- Catálogo verificado: 64 equipos y 1.024 jugadores, con referencias válidas.
- Sintaxis JavaScript verificada con Node.
- Prueba de comportamiento del front con DOM y HTTP simulados: catálogo,
  próximos cruces, historial, validación de rivales, guardado e inicio del
  partido correcto. Comando opcional: `node tests/frontend_match_navigation.cjs`.

La vista previa del navegador no pudo conectarse al servidor de prueba.
No se ejecutó aquí la validación integral sobre tus contenedores Docker.
El chequeo de endpoints y la revisión visual se completan después de aplicar
el paquete en tu entorno. Las pruebas con dobles no sustituyen esa ejecución.
