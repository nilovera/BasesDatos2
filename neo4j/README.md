# Neo4j — proyección de relaciones

Neo4j modela los recorridos que no resultan naturales sobre documentos aislados.
MongoDB continúa siendo la fuente autoritativa; el grafo es una proyección
idempotente del catálogo común.

## Modelo

- `Jugador -[:PERTENECE_A]-> Equipo`
- `Equipo -[:MIEMBRO_DE]-> Confederacion`
- `Confederacion -[:PARTICIPA_EN]-> Torneo`
- `Equipo -[:LOCAL_EN|VISITANTE_EN]-> Partido`
- `Partido -[:FORMA_PARTE_DE]-> Torneo`

El catálogo inicial genera 64 equipos, 1.024 jugadores, un partido de
demostración, las confederaciones presentes y el torneo `TOR-2030`.

## Seguridad y persistencia

La imagen está fijada en `neo4j:5.26.34-community-trixie`. La contraseña se
genera localmente en `.secretos/`, se monta como Docker secret y nunca se
versiona. Los datos, logs e importaciones utilizan volúmenes nombrados.

## Acceso

- Browser: `http://localhost:7474`
- Bolt: `bolt://localhost:7687`
- Usuario: `neo4j`
- Contraseña: `.secretos/neo4j-password.txt` (no compartir ni versionar)

## Pruebas

```text
powershell -ExecutionPolicy Bypass -File scripts\verificar_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_grafo_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_neo4j.ps1
```

Las consultas manuales de CRUD y recorridos están en `neo4j/queries/`.
No usar `docker compose down -v`: eliminaría los volúmenes persistentes.


## Proyección deportiva y ejecución

Outbox incorpora nodos `EventoOficial` y relaciones de gol, asistencia, tarjeta,
VAR y sustitución, identificadas por evento. El worker actualiza Redis y Neo4j
antes de confirmar la publicación. El grafo no constituye la autoridad del
marcador ni una reconciliación completa de todas las correcciones históricas.

La ejecución Docker y la falla controlada están registradas. La simulación
integrada verificó relaciones deportivas. Ver [estado de validación](../docs/estado_validacion.md).
