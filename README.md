# Hito 9 - Entidades complejas con InterSystems IRIS

Implementación del módulo orientado a objetos de Fixture 2030 mediante InterSystems IRIS Community Edition.

## Modelo

- `Fixture.Persona`: clase persistente base.
- `Fixture.Arbitro` y `Fixture.Tecnico`: especializaciones persistentes.
- `Fixture.Partido`: raíz del agregado.
- `Fixture.EventoPartido`: hijo subordinado mediante relación `parent/children`.
- Índice único por código de partido e índice sobre la relación del extremo hijo.
- Validaciones encapsuladas para estados, eventos y equipos participantes.

## Requisitos

- Docker Desktop con integración WSL 2 para Ubuntu.
- Carpeta durable obligatoria: `~/docker/data/iris`.
- Puertos locales `1972` y `52773` disponibles.

## Preparación del volumen durable

Desde PowerShell:

```powershell
wsl -d Ubuntu -- mkdir -p /home/nicol/docker/data/iris
wsl -d Ubuntu -u root -- chown -R 51773:51773 /home/nicol/docker/data/iris
wsl -d Ubuntu -u root -- chmod -R 777 /home/nicol/docker/data/iris
```

El UID `51773` corresponde al usuario interno `irisowner` de la imagen utilizada.

## Inicio y verificación

```powershell
wsl -d Ubuntu -- bash -lc 'cd /mnt/c/fixture2030-iris && docker compose up -d'
wsl -d Ubuntu -- bash -lc 'cd /mnt/c/fixture2030-iris && docker compose ps'
```

El servicio debe aparecer como `healthy`.

## Carga de clases

La clase base debe cargarse antes que sus subclases. Las clases relacionadas se cargan primero como definición y luego se compilan juntas.

```powershell
@(
    'Do $system.OBJ.Load("/scripts/Fixture.Persona.cls","ck")'
    'Do $system.OBJ.Load("/scripts/Fixture.Arbitro.cls","ck")'
    'Do $system.OBJ.Load("/scripts/Fixture.Tecnico.cls","ck")'
    'Do $system.OBJ.Load("/scripts/Fixture.Partido.cls","k")'
    'Do $system.OBJ.Load("/scripts/Fixture.EventoPartido.cls","ck")'
    'Do $system.OBJ.Load("/scripts/Fixture.Partido.cls","ck")'
    'Halt'
) | wsl -d Ubuntu -- docker exec -i fixture2030-iris iris session IRIS
```

## Demostración reproducible

Cargar y ejecutar la rutina:

```powershell
@(
    'Do $system.OBJ.Load("/scripts/demo_crud_iris_fixture2030.mac","ck")'
    'Do Main^FixtureDemo'
    'Halt'
) | wsl -d Ubuntu -- docker exec -i fixture2030-iris iris session IRIS
```

La rutina demuestra `%New()`, `%Save()`, `%OpenId()`, herencia, guardado padre-hijo con un solo `%Save()` y validaciones controladas. Debe ejecutarse sobre una instancia limpia o utilizando otros códigos de demostración, porque existen índices únicos.

## Persistencia

Para detener sin perder datos:

```powershell
wsl -d Ubuntu -- bash -lc 'cd /mnt/c/fixture2030-iris && docker compose down'
```

No se incluye la data raw de IRIS en el repositorio. Solo se versionan clases, rutina, documentación, configuración y evidencias.

## Evidencias y documentación

- `docs/diseno_dominio.md`: entidades, diagrama, matriz de integridad y patrones de acceso.
- `docs/resultados_pruebas.md`: resultados observados.
- `docs/evidencia/`: capturas de compilación, persistencia, SQL, navegación y validaciones.
