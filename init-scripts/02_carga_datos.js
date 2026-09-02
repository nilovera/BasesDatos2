// ======================================================
// Fixture 2030 - Hito 4
// Carga reproducible de Equipos y Jugadores
// ======================================================

db = db.getSiblingDB("fixture2030");


// ======================================================
// 1. CARGA DE 64 EQUIPOS
// ======================================================

const confederaciones = [
  "CONMEBOL",
  "UEFA",
  "CONCACAF",
  "CAF",
  "AFC",
  "OFC"
];

const equiposOps = [];

for (let i = 1; i <= 64; i++) {

  const numero = String(i).padStart(2, "0");
  const equipoId = "EQ-" + numero;

  equiposOps.push({
    updateOne: {
      filter: { _id: equipoId },

      update: {
        $set: {
          nombre: "Equipo " + numero,
          confederacion:
            confederaciones[(i - 1) % confederaciones.length],
          ranking: i
        }
      },

      upsert: true
    }
  });
}

db.equipos.bulkWrite(equiposOps);

print("64 equipos procesados.");


// ======================================================
// 2. CARGA DE 1.024 JUGADORES
// ======================================================

const posiciones = [
  "Arquero",
  "Defensor",
  "Mediocampista",
  "Delantero"
];

const jugadoresOps = [];

let jugadorNumero = 1;

for (let equipo = 1; equipo <= 64; equipo++) {

  const equipoNumero =
    String(equipo).padStart(2, "0");

  const equipoId =
    "EQ-" + equipoNumero;

  for (let j = 1; j <= 16; j++) {

    const jugadorId =
      "JUG-" +
      String(jugadorNumero).padStart(4, "0");

    const anio =
      1990 + (jugadorNumero % 15);

    const mes =
      String((jugadorNumero % 12) + 1).padStart(2, "0");

    const dia =
      String((jugadorNumero % 28) + 1).padStart(2, "0");

    jugadoresOps.push({
      updateOne: {
        filter: {
          _id: jugadorId
        },

        update: {
          $set: {
            nombre:
              "Jugador " +
              String(jugadorNumero).padStart(4, "0"),

            fecha_nacimiento:
              new Date(
                anio + "-" +
                mes + "-" +
                dia + "T00:00:00Z"
              ),

            posicion:
              posiciones[(j - 1) % posiciones.length],

            equipo_id:
              equipoId
          }
        },

        upsert: true
      }
    });

    jugadorNumero++;
  }
}

db.jugadores.bulkWrite(jugadoresOps);

print("1024 jugadores procesados.");


// ======================================================
// 3. VERIFICACIÓN
// ======================================================

print(
  "Cantidad de equipos:",
  db.equipos.countDocuments()
);

print(
  "Cantidad de jugadores:",
  db.jugadores.countDocuments()
);

print(
  "Carga reproducible finalizada correctamente."
);