/* global db, Long */

// Carga idempotente del catálogo común. Ejecutar después de 01_schema.js.

const fs = require("fs");
const path = require("path");

db = db.getSiblingDB("fixture2030");

const catalogRoot = process.env.CATALOG_ROOT || "/opt/fixture2030/catalogo";

function readJson(fileName) {
  const fullPath = path.join(catalogRoot, fileName);
  return JSON.parse(fs.readFileSync(fullPath, "utf8"));
}

const equipos = readJson("equipos.json");
const jugadores = readJson("jugadores.json");
const partidos = readJson("partidos.json");
const equivalencias = readJson("equivalencias_codigos.json");

if (equipos.length !== 64) {
  throw new Error(`Se esperaban 64 equipos y se recibieron ${equipos.length}`);
}
if (jugadores.length !== 1024) {
  throw new Error(`Se esperaban 1024 jugadores y se recibieron ${jugadores.length}`);
}
if (partidos.length < 1) {
  throw new Error("El catálogo debe contener al menos un partido de demostración");
}

const externalCodeByTeam = Object.fromEntries(
  Object.entries(equivalencias).map(([externalCode, teamId]) => [teamId, externalCode])
);

const positionMap = {
  Arquero: "ARQUERO",
  Defensor: "DEFENSOR",
  Mediocampista: "MEDIOCAMPISTA",
  Delantero: "DELANTERO"
};

const now = new Date();

db.equipos.bulkWrite(
  equipos.map((team) => {
    const document = {
      equipoId: team._id,
      nombre: team.nombre,
      confederacion: team.confederacion,
      ranking: NumberInt(team.ranking),
      activo: true,
      actualizadoEn: now
    };
    if (externalCodeByTeam[team._id]) {
      document.codigoExterno = externalCodeByTeam[team._id];
    }
    return {
      updateOne: {
        filter: { _id: team._id },
        update: {
          $set: document,
          $setOnInsert: { creadoEn: now }
        },
        upsert: true
      }
    };
  }),
  { ordered: true }
);

db.jugadores.bulkWrite(
  jugadores.map((player) => {
    const position = positionMap[player.posicion];
    if (!position) {
      throw new Error(`Posición no soportada para ${player._id}: ${player.posicion}`);
    }
    return {
      updateOne: {
        filter: { _id: player._id },
        update: {
          $set: {
            jugadorId: player._id,
            equipoId: player.equipo_id,
            nombre: player.nombre,
            posicion: position,
            fechaNacimiento: new Date(player.fecha_nacimiento),
            activo: true,
            actualizadoEn: now
          },
          $setOnInsert: { creadoEn: now }
        },
        upsert: true
      }
    };
  }),
  { ordered: true }
);

db.partidos.bulkWrite(
  partidos.map((match) => ({
    updateOne: {
      filter: { _id: match._id },
      update: {
        $set: {
          partidoId: match._id,
          equipos: {
            localId: match.equipo_local_id,
            visitanteId: match.equipo_visitante_id
          },
          inicioProgramado: new Date(match.inicio_programado),
          inicioReal: null,
          finReal: null,
          estado: match.estado,
          marcador: { local: NumberInt(0), visitante: NumberInt(0) },
          alineaciones: {
            local: { titulares: [], suplentes: [] },
            visitante: { titulares: [], suplentes: [] }
          },
          ultimaSecuencia: Long(0),
          version: Long(1),
          actualizadoEn: now
        },
        $setOnInsert: { creadoEn: now }
      },
      upsert: true
    }
  })),
  { ordered: true }
);

printjson({
  carga: "catalogo_fixture2030",
  equipos: db.equipos.countDocuments({}),
  jugadores: db.jugadores.countDocuments({}),
  partidos: db.partidos.countDocuments({}),
  ejecutadoEn: now
});
