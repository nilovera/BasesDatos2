// ======================================================
// Fixture 2030 - Hito 4
// Operaciones y consultas sobre Equipos y Jugadores
// ======================================================

db = db.getSiblingDB("fixture2030");


// ======================================================
// 1. INSERCIÓN DE UN EQUIPO
// Objetivo: demostrar la incorporación de un equipo nuevo.
// ======================================================

db.equipos.updateOne(
  { _id: "EQ-TEST" },
  {
    $set: {
      nombre: "Equipo de Prueba",
      confederacion: "TEST",
      ranking: 100
    }
  },
  { upsert: true }
);


// ======================================================
// 2. INSERCIÓN DE UN JUGADOR
// Objetivo: demostrar la incorporación de un jugador
// relacionado con un equipo existente.
// ======================================================

db.jugadores.updateOne(
  { _id: "JUG-TEST" },
  {
    $set: {
      nombre: "Jugador de Prueba",
      fecha_nacimiento: new Date("2000-01-01T00:00:00Z"),
      posicion: "Delantero",
      equipo_id: "EQ-TEST"
    }
  },
  { upsert: true }
);


// ======================================================
// 3. RECUPERACIÓN POR IDENTIFICADOR - EQUIPO
// ======================================================

print("Equipo buscado por identificador:");

printjson(
  db.equipos.findOne({
    _id: "EQ-TEST"
  })
);


// ======================================================
// 4. RECUPERACIÓN POR IDENTIFICADOR - JUGADOR
// ======================================================

print("Jugador buscado por identificador:");

printjson(
  db.jugadores.findOne({
    _id: "JUG-TEST"
  })
);


// ======================================================
// 5. ACTUALIZACIÓN DE EQUIPO
// Objetivo: modificar información sin cambiar su identidad.
// ======================================================

db.equipos.updateOne(
  { _id: "EQ-TEST" },
  {
    $set: {
      ranking: 90
    }
  }
);


// ======================================================
// 6. ACTUALIZACIÓN DE JUGADOR
// ======================================================

db.jugadores.updateOne(
  { _id: "JUG-TEST" },
  {
    $set: {
      posicion: "Mediocampista"
    }
  }
);


// ======================================================
// 7. VERIFICACIÓN DE ACTUALIZACIONES
// ======================================================

print("Equipo después de actualización:");
printjson(
  db.equipos.findOne({
    _id: "EQ-TEST"
  })
);

print("Jugador después de actualización:");
printjson(
  db.jugadores.findOne({
    _id: "JUG-TEST"
  })
);


// ======================================================
// 8. RECUPERACIÓN FILTRADA
// Objetivo: obtener jugadores de un equipo específico.
// ======================================================

print("Jugadores del equipo EQ-01:");

db.jugadores
  .find({
    equipo_id: "EQ-01"
  })
  .forEach(printjson);


// ======================================================
// 9. PROYECCIÓN
// Objetivo: devolver únicamente los campos necesarios.
// ======================================================

print("Proyección de jugadores:");

db.jugadores
  .find(
    { equipo_id: "EQ-01" },
    {
      _id: 1,
      nombre: 1,
      posicion: 1,
      equipo_id: 1
    }
  )
  .limit(5)
  .forEach(printjson);


// ======================================================
// 10. ORDENAMIENTO
// Objetivo: recuperar jugadores ordenados por nombre.
// ======================================================

print("Jugadores ordenados por nombre:");

db.jugadores
  .find({
    equipo_id: "EQ-01"
  })
  .sort({
    nombre: 1
  })
  .limit(5)
  .forEach(printjson);


// ======================================================
// 11. PAGINACIÓN
// Objetivo: simular una interfaz que muestra 5 jugadores
// por página.
// Página 2 = saltar los primeros 5 y mostrar los siguientes 5.
// ======================================================

print("Página 2 de jugadores:");

db.jugadores
  .find({})
  .sort({
    _id: 1
  })
  .skip(5)
  .limit(5)
  .forEach(printjson);


// ======================================================
// 12. AGREGACIÓN
// Objetivo: conocer cuántos jugadores hay por equipo.
// ======================================================

print("Cantidad de jugadores por equipo:");

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
]).forEach(printjson);


// ======================================================
// FIN
// ======================================================

print("Operaciones y consultas ejecutadas correctamente.");