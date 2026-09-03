# Hito 4 - Módulo Documental MongoDB Fixture 2030

## Ingeniería de Datos II

Este proyecto implementa el módulo documental de **Equipos y Jugadores del Fixture 2030** utilizando MongoDB.

El objetivo es persistir, recuperar y actualizar información de equipos y jugadores mediante una base de datos documental, utilizando Docker para disponer de un entorno reproducible y portable.

---

## 1. Tecnologías utilizadas

- MongoDB 7.x
- Docker
- Docker Compose
- Mongosh
- MongoDB Compass
- Mongo Express

---

## 2. Estructura del proyecto

```text
fixture2030-mongodb/
│
├── docker-compose.yml
├── README.md
│
├── init-scripts/
│   └── 02_carga_datos.js
│
├── schemas/
│   └── 01_validaciones.js
│
├── queries/
│   ├── 01_operaciones_consultas.js
│   └── 02_indices_rendimiento.js
│
└── docs/
```

### Descripción de los archivos

**docker-compose.yml**

Configura el entorno Docker utilizado para ejecutar MongoDB y Mongo Express. También define el volumen utilizado para mantener persistidos los datos de MongoDB.

**schemas/01_validaciones.js**

Crea las colecciones `equipos` y `jugadores` en caso de que no existan y define reglas de validación sobre sus campos principales.

**init-scripts/02_carga_datos.js**

Realiza la carga inicial del módulo documental. Genera:

- 64 equipos.
- 1024 jugadores.
- 16 jugadores por equipo.

La carga utiliza operaciones `upsert`, por lo que puede ejecutarse nuevamente sin generar registros duplicados.

**queries/01_operaciones_consultas.js**

Contiene las operaciones requeridas por el Hito 4:

- Inserción de equipos y jugadores.
- Recuperación por identificador.
- Recuperación filtrada.
- Proyección.
- Ordenamiento.
- Paginación.
- Actualización.
- Agregación.

**queries/02_indices_rendimiento.js**

Analiza el comportamiento de una consulta antes y después de crear un índice sobre el campo `equipo_id` de la colección `jugadores`, utilizando `explain("executionStats")`.

---

## 3. Modelo documental

El módulo utiliza dos colecciones principales: `equipos` y `jugadores`.

### Colección equipos

Ejemplo de documento:

```javascript
{
  _id: "EQ-01",
  nombre: "Equipo 01",
  confederacion: "CONMEBOL",
  ranking: 1
}
```

Campos principales:

- `_id`: identificador único del equipo.
- `nombre`: nombre del equipo.
- `confederacion`: confederación a la que pertenece.
- `ranking`: posición de ranking utilizada en los datos de prueba.

### Colección jugadores

Ejemplo de documento:

```javascript
{
  _id: "JUG-0001",
  nombre: "Jugador 0001",
  fecha_nacimiento: ISODate("1991-02-02T00:00:00.000Z"),
  posicion: "Arquero",
  equipo_id: "EQ-01"
}
```

Campos principales:

- `_id`: identificador único del jugador.
- `nombre`: nombre del jugador.
- `fecha_nacimiento`: fecha de nacimiento.
- `posicion`: posición del jugador.
- `equipo_id`: identificador del equipo al que pertenece.

---

## 4. Relación entre equipos y jugadores

La relación se implementa mediante **referencing**.

Cada jugador almacena en `equipo_id` el identificador del equipo al que pertenece.

Ejemplo:

```javascript
equipo_id: "EQ-01"
```

La información completa del equipo no se duplica dentro de cada jugador.

Esta estrategia permite mantener equipos y jugadores como documentos independientes y actualizar la información de cada entidad sin tener que modificar documentos embebidos en múltiples ubicaciones.

La justificación completa de esta decisión se desarrolla en el documento de decisiones técnicas del Hito 4.

---

## 5. Identificadores

Para los datos sintéticos se utilizan identificadores estables y simples.

### Equipos

```text
EQ-01
EQ-02
...
EQ-64
```

### Jugadores

```text
JUG-0001
JUG-0002
...
JUG-1024
```

Estos identificadores permiten relacionar documentos de manera clara y reproducible.

---

## 6. Requisitos previos

Para ejecutar el proyecto es necesario contar con:

- Docker Desktop.
- Docker Compose.

MongoDB Compass es opcional y puede utilizarse para inspeccionar las colecciones, ejecutar consultas y visualizar los datos.

---

## 7. Levantar el entorno

Desde una terminal ubicada en la carpeta raíz del proyecto ejecutar:

```powershell
docker compose up -d
```

Para comprobar el estado de los servicios:

```powershell
docker compose ps
```

MongoDB queda disponible en:

```text
localhost:27017
```

Mongo Express queda disponible en:

```text
http://localhost:8081
```

---

## 8. Conexión a MongoDB

La configuración utilizada en el entorno local es:

```text
Host: localhost
Puerto: 27017
Usuario: admin
Contraseña: password123
Authentication Database: admin
```

Estas credenciales se utilizan únicamente para el entorno académico local del proyecto.

### Acceso mediante Mongosh

Ejecutar:

```powershell
docker exec -it fixture2030-mongodb mongosh --username admin --password password123 --authenticationDatabase admin
```

Una vez dentro de Mongosh:

```javascript
db = db.getSiblingDB("fixture2030");
```

---

## 9. Creación de colecciones y validaciones

Primero se copia el script al contenedor:

```powershell
docker cp .\schemas\01_validaciones.js fixture2030-mongodb:/tmp/01_validaciones.js
```

Luego se ejecuta:

```powershell
docker exec -it fixture2030-mongodb mongosh --username admin --password password123 --authenticationDatabase admin /tmp/01_validaciones.js
```

El script crea o actualiza las validaciones de las colecciones:

```text
equipos
jugadores
```

Las validaciones controlan la presencia y el tipo de los campos críticos.

En `equipos` se validan principalmente:

- `_id`
- `nombre`
- `confederacion`
- `ranking`

En `jugadores` se validan principalmente:

- `_id`
- `nombre`
- `fecha_nacimiento`
- `posicion`
- `equipo_id`

Durante las pruebas se comprobó además que un documento incompleto es rechazado por MongoDB.

---

## 10. Carga inicial

Copiar el script de carga al contenedor:

```powershell
docker cp .\init-scripts\02_carga_datos.js fixture2030-mongodb:/tmp/02_carga_datos.js
```

Ejecutarlo:

```powershell
docker exec -it fixture2030-mongodb mongosh --username admin --password password123 --authenticationDatabase admin /tmp/02_carga_datos.js
```

Al finalizar deben existir:

```text
64 equipos
1024 jugadores
```

La carga genera 16 jugadores por equipo.

### Reproducibilidad e idempotencia

El script utiliza operaciones `upsert`.

Por este motivo puede ejecutarse varias veces sin generar duplicados.

La prueba realizada consistió en ejecutar la carga dos veces y comprobar que las cantidades finales continuaran siendo:

```text
64 equipos
1024 jugadores
```

Esto permite reproducir la carga sin producir inconsistencias por duplicación.

---

## 11. Datos sintéticos

Los datos utilizados son **sintéticos**.

Esto significa que fueron generados para probar el funcionamiento del módulo y no representan los planteles definitivos del Mundial 2030.

La utilización de datos sintéticos permite contar con un conjunto:

- reproducible;
- consistente;
- suficiente para cumplir el volumen mínimo solicitado;
- independiente de información futura todavía no disponible.

---

## 12. Verificación de integridad entre jugadores y equipos

MongoDB no crea automáticamente una clave foránea entre `jugadores.equipo_id` y `equipos._id`.

Por este motivo se realizó una verificación mediante `$lookup` para detectar jugadores relacionados con equipos inexistentes.

```javascript
db.jugadores.aggregate([
  {
    $lookup: {
      from: "equipos",
      localField: "equipo_id",
      foreignField: "_id",
      as: "equipo"
    }
  },
  {
    $match: {
      equipo: { $size: 0 }
    }
  }
]);
```

Si la consulta devuelve 0 documentos significa que no existen jugadores huérfanos.

En las pruebas realizadas el resultado fue:

```text
0 jugadores huérfanos
```

---

## 13. Operaciones y consultas

Las operaciones principales se encuentran en:

```text
queries/01_operaciones_consultas.js
```

Para ejecutarlas:

```powershell
docker cp .\queries\01_operaciones_consultas.js fixture2030-mongodb:/tmp/01_operaciones_consultas.js
```

Luego:

```powershell
docker exec -it fixture2030-mongodb mongosh --username admin --password password123 --authenticationDatabase admin /tmp/01_operaciones_consultas.js
```

El script implementa las operaciones mínimas solicitadas.

### 13.1 Inserción

Se incorpora un nuevo equipo y un nuevo jugador.

Los documentos de prueba utilizados son:

```text
EQ-TEST
JUG-TEST
```

El jugador queda relacionado con el equipo mediante `equipo_id`.

---

### 13.2 Recuperación por identificador

Se recuperan un equipo y un jugador utilizando sus respectivos valores de `_id`.

Ejemplo:

```javascript
db.equipos.findOne({ _id: "EQ-TEST" });
```

```javascript
db.jugadores.findOne({ _id: "JUG-TEST" });
```

---

### 13.3 Recuperación filtrada

Se recuperan los jugadores pertenecientes a un equipo determinado.

Ejemplo:

```javascript
db.jugadores.find({
  equipo_id: "EQ-01"
});
```

Esta consulta representa una condición de negocio frecuente del módulo: consultar el plantel correspondiente a un equipo.

---

### 13.4 Proyección

Se devuelven solamente los atributos necesarios para una consulta concreta.

Ejemplo:

```javascript
db.jugadores.find(
  { equipo_id: "EQ-01" },
  {
    _id: 1,
    nombre: 1,
    posicion: 1,
    equipo_id: 1
  }
);
```

La proyección evita devolver información que no es necesaria para la consulta.

---

### 13.5 Ordenamiento

Los jugadores pueden recuperarse ordenados por nombre.

Ejemplo:

```javascript
db.jugadores
  .find({ equipo_id: "EQ-01" })
  .sort({ nombre: 1 });
```

---

### 13.6 Paginación

Se utiliza `skip()` junto con `limit()` para recuperar resultados por páginas.

Ejemplo:

```javascript
db.jugadores
  .find({})
  .sort({ _id: 1 })
  .skip(5)
  .limit(5);
```

La paginación es útil para una interfaz de consulta porque evita devolver todos los registros de una colección de una sola vez y permite presentar los resultados en bloques manejables.

---

### 13.7 Actualización

Se modifica información de un equipo y de un jugador sin cambiar sus identificadores ni romper la relación entre documentos.

En las pruebas se actualizó:

- el `ranking` de un equipo;
- la `posicion` de un jugador.

---

### 13.8 Agregación

Se utiliza un pipeline de agregación para obtener una visión consolidada de la cantidad de jugadores por equipo.

Ejemplo:

```javascript
db.jugadores.aggregate([
  {
    $group: {
      _id: "$equipo_id",
      cantidadJugadores: {
        $sum: 1
      }
    }
  },
  {
    $sort: {
      _id: 1
    }
  }
]);
```

Esta consulta permite analizar la distribución de jugadores entre los distintos equipos.

---

## 14. Índices y análisis de rendimiento

Para evaluar el impacto de una decisión de indexación se utiliza la consulta:

```javascript
db.jugadores.find({
  equipo_id: "EQ-01"
});
```

Esta consulta se considera relevante porque recuperar los jugadores de un equipo es una operación frecuente dentro del módulo.

El análisis se encuentra en:

```text
queries/02_indices_rendimiento.js
```

Para ejecutarlo:

```powershell
docker cp .\queries\02_indices_rendimiento.js fixture2030-mongodb:/tmp/02_indices_rendimiento.js
```

Luego:

```powershell
docker exec -it fixture2030-mongodb mongosh --username admin --password password123 --authenticationDatabase admin /tmp/02_indices_rendimiento.js
```

El script:

1. elimina el índice de prueba si ya existe;
2. ejecuta la consulta sin índice;
3. obtiene `explain("executionStats")`;
4. crea el índice sobre `equipo_id`;
5. vuelve a ejecutar la misma consulta;
6. compara los resultados.

El índice creado es:

```javascript
db.jugadores.createIndex(
  { equipo_id: 1 },
  { name: "idx_jugadores_equipo" }
);
```

### Resultado antes del índice

```text
stage: COLLSCAN
nReturned: 16
totalKeysExamined: 0
totalDocsExamined: 1025
```

MongoDB realizó un `COLLSCAN`, por lo que tuvo que recorrer prácticamente toda la colección para recuperar los 16 jugadores de `EQ-01`.

### Resultado después del índice

```text
stagePrincipal: FETCH
stageIndice: IXSCAN
indiceUtilizado: idx_jugadores_equipo
nReturned: 16
totalKeysExamined: 16
totalDocsExamined: 16
```

Luego de crear el índice, MongoDB utilizó `IXSCAN` y examinó únicamente los 16 documentos correspondientes.

La comparación demuestra una reducción de:

```text
1025 documentos examinados
a
16 documentos examinados
```

Los tiempos de ejecución en milisegundos no son el criterio principal de comparación debido al volumen reducido de datos utilizado para la práctica. La evidencia principal se obtiene del plan de ejecución y de la cantidad de documentos examinados.

La justificación técnica completa del índice se encuentra en el documento de decisiones documentales.

---

## 15. Persistencia

MongoDB utiliza un volumen Docker para mantener la información almacenada aunque el contenedor sea detenido.

El volumen definido para los datos de MongoDB es:

```text
mongodb_data
```

El entorno puede detenerse mediante:

```powershell
docker compose down
```

y volver a iniciarse con:

```powershell
docker compose up -d
```

sin perder los datos almacenados.

Para conservar los datos no debe utilizarse:

```powershell
docker compose down -v
```

ya que la opción `-v` elimina los volúmenes asociados.

---

## 16. Detener y reiniciar el entorno

Detener:

```powershell
docker compose down
```

Iniciar nuevamente:

```powershell
docker compose up -d
```

Comprobar el estado:

```powershell
docker compose ps
```

La base de datos continúa disponible gracias al volumen persistente.

---

## 17. Evidencias

Durante el desarrollo se generaron evidencias de:

- MongoDB ejecutándose correctamente mediante Docker.
- Conexión mediante MongoDB Compass.
- Creación de las colecciones.
- Reglas de validación.
- Rechazo de documentos inválidos.
- Carga de 64 equipos y 1024 jugadores.
- Segunda ejecución de la carga sin duplicaciones.
- Verificación de inexistencia de jugadores huérfanos.
- Ejecución de operaciones y consultas.
- Agregación.
- Análisis de rendimiento antes y después de crear el índice.

En particular, para la consulta por `equipo_id` se registró:

```text
ANTES
COLLSCAN
1025 documentos examinados

DESPUÉS
IXSCAN
16 documentos examinados
```

---

## 18. Decisiones técnicas

Las decisiones de diseño se documentan de forma separada en:

```text
Grupo_10_Hito_4_Decisiones_Documentales_Fixture2030.md
```

El documento desarrolla:

- estrategia de relación entre equipos y jugadores;
- validación documental;
- estrategia de identificadores;
- índices principales;
- estrategia de carga y actualización;
- alternativas consideradas;
- elección realizada;
- justificación;
- impacto esperado;
- trazabilidad con los Hitos 2 y 3.

---

## 19. Relación con Hito 2 y Hito 3

La implementación mantiene la decisión de utilizar MongoDB para la información documental de equipos y jugadores definida en los hitos anteriores.

El módulo se concentra en información relativamente estable de estas entidades y utiliza identificadores lógicos que pueden ser utilizados por otros subsistemas del Fixture 2030.

La arquitectura general continúa siendo políglota: MongoDB se utiliza para este módulo documental mientras que otros tipos de información del sistema pueden persistirse utilizando tecnologías diferentes según sus características y necesidades.

El detalle y la justificación de esta trazabilidad se desarrollan en el documento de decisiones técnicas.

---

## 20. Limitaciones conocidas

- Los datos de equipos y jugadores son sintéticos y no representan los planteles definitivos del Mundial 2030.
- MongoDB no aplica automáticamente integridad referencial entre `jugadores.equipo_id` y `equipos._id`. La coherencia se comprueba mediante el proceso de carga y consultas de validación.
- La implementación se concentra únicamente en la persistencia documental de equipos y jugadores.
- No se incluye una API REST ni una interfaz gráfica propia, ya que no forman parte del alcance obligatorio del Hito 4.
- Las pruebas de rendimiento se realizan sobre un volumen académico de aproximadamente 1000 jugadores. Por este motivo los tiempos en milisegundos pueden variar y no son suficientes por sí solos para evaluar el impacto del índice.
- La evidencia de mejora de rendimiento se basa principalmente en el plan de ejecución y en la reducción de documentos examinados.

---

## 21. Resultado final

El módulo implementado permite:

- levantar MongoDB mediante Docker Compose;
- mantener los datos persistidos mediante un volumen;
- almacenar equipos y jugadores en colecciones documentales;
- relacionar jugadores con equipos mediante referencias;
- validar campos críticos;
- cargar 64 equipos y 1024 jugadores;
- repetir la carga sin generar duplicados;
- verificar la integridad de las relaciones;
- insertar nuevos documentos;
- recuperar información por identificador;
- ejecutar filtros;
- utilizar proyecciones;
- ordenar y paginar resultados;
- actualizar equipos y jugadores;
- ejecutar agregaciones;
- crear índices;
- comparar planes de ejecución mediante `explain("executionStats")`;
- reproducir las principales operaciones del módulo desde scripts incluidos en el repositorio.
