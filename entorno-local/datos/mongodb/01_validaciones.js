// ======================================================
// Fixture 2030 - Hito 4
// Validaciones documentales de Equipos y Jugadores
// ======================================================

// Seleccionar la base de datos del proyecto
db = db.getSiblingDB("fixture2030");


// ======================================================
// COLECCIÓN: equipos
// ======================================================

const equiposValidator = {
  $jsonSchema: {
    bsonType: "object",
    required: [
      "_id",
      "nombre",
      "confederacion",
      "ranking"
    ],
    properties: {
      _id: {
        bsonType: "string",
        description: "Identificador único del equipo"
      },
      nombre: {
        bsonType: "string",
        description: "Nombre de la selección"
      },
      confederacion: {
        bsonType: "string",
        description: "Confederación a la que pertenece el equipo"
      },
      ranking: {
        bsonType: ["int", "long", "double", "decimal"],
        minimum: 1,
        description: "Posición del equipo en el ranking"
      }
    }
  }
};


// Crear equipos si no existe.
// Si ya existe, actualizar sus reglas de validación.
if (!db.getCollectionNames().includes("equipos")) {

  db.createCollection("equipos", {
    validator: equiposValidator,
    validationLevel: "strict",
    validationAction: "error"
  });

  print("Colección equipos creada correctamente.");

} else {

  db.runCommand({
    collMod: "equipos",
    validator: equiposValidator,
    validationLevel: "strict",
    validationAction: "error"
  });

  print("Validación de equipos actualizada correctamente.");
}


// ======================================================
// COLECCIÓN: jugadores
// ======================================================

const jugadoresValidator = {
  $jsonSchema: {
    bsonType: "object",
    required: [
      "_id",
      "nombre",
      "fecha_nacimiento",
      "posicion",
      "equipo_id"
    ],
    properties: {
      _id: {
        bsonType: "string",
        description: "Identificador único del jugador"
      },
      nombre: {
        bsonType: "string",
        description: "Nombre completo del jugador"
      },
      fecha_nacimiento: {
        bsonType: "date",
        description: "Fecha de nacimiento del jugador"
      },
      posicion: {
        bsonType: "string",
        description: "Posición deportiva del jugador"
      },
      equipo_id: {
        bsonType: "string",
        description: "Referencia al _id del equipo al que pertenece"
      }
    }
  }
};


// Crear jugadores si no existe.
// Si ya existe, actualizar sus reglas de validación.
if (!db.getCollectionNames().includes("jugadores")) {

  db.createCollection("jugadores", {
    validator: jugadoresValidator,
    validationLevel: "strict",
    validationAction: "error"
  });

  print("Colección jugadores creada correctamente.");

} else {

  db.runCommand({
    collMod: "jugadores",
    validator: jugadoresValidator,
    validationLevel: "strict",
    validationAction: "error"
  });

  print("Validación de jugadores actualizada correctamente.");
}


print("Validaciones del Fixture 2030 configuradas correctamente.");