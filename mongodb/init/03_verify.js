/* global db */

db = db.getSiblingDB("fixture2030");

function assertEqual(actual, expected, label) {
  if (actual !== expected) {
    throw new Error(`${label}: esperado=${expected}, actual=${actual}`);
  }
}

const hello = db.getSiblingDB("admin").runCommand({ hello: 1 });
if (hello.setName !== "rs0" || hello.isWritablePrimary !== true) {
  throw new Error("MongoDB no está operativo como PRIMARY de rs0");
}

assertEqual(db.equipos.countDocuments({}), 64, "cantidad de equipos");
assertEqual(db.jugadores.countDocuments({}), 1024, "cantidad de jugadores");
assertEqual(
  db.partidos.countDocuments({ _id: "PAR-0001" }),
  1,
  "partido de demostración PAR-0001"
);

const eventCount = db.eventos_oficiales.countDocuments({});
const outboxCount = db.outbox.countDocuments({});
assertEqual(outboxCount, eventCount, "una salida de Outbox por evento");

const match = db.partidos.findOne({ _id: "PAR-0001" });
const matchEventCount = db.eventos_oficiales.countDocuments({ partidoId: "PAR-0001" });
assertEqual(Number(match.ultimaSecuencia), matchEventCount, "secuencia del partido");

const orphanEvents = db.eventos_oficiales.aggregate([
  {
    $lookup: {
      from: "partidos",
      localField: "partidoId",
      foreignField: "partidoId",
      as: "partido"
    }
  },
  { $match: { partido: { $size: 0 } } },
  { $count: "total" }
]).toArray();
assertEqual(orphanEvents.length === 0 ? 0 : orphanEvents[0].total, 0, "eventos huérfanos");

const orphanPlayers = db.jugadores.aggregate([
  {
    $lookup: {
      from: "equipos",
      localField: "equipoId",
      foreignField: "equipoId",
      as: "equipo"
    }
  },
  { $match: { equipo: { $size: 0 } } },
  { $count: "total" }
]).toArray();

assertEqual(orphanPlayers.length === 0 ? 0 : orphanPlayers[0].total, 0, "jugadores huérfanos");

const requiredIndexes = {
  eventos_oficiales: [
    "uq_eventos_eventoId",
    "uq_eventos_partido_secuencia",
    "uq_eventos_idempotencia"
  ],
  outbox: ["uq_outbox_eventoId", "ix_outbox_pendientes", "ttl_outbox_publicada"]
};

for (const [collectionName, indexNames] of Object.entries(requiredIndexes)) {
  const actualNames = new Set(db.getCollection(collectionName).getIndexes().map((index) => index.name));
  for (const indexName of indexNames) {
    if (!actualNames.has(indexName)) {
      throw new Error(`Falta índice ${collectionName}.${indexName}`);
    }
  }
}

printjson({
  estado: "OK",
  replicaSet: hello.setName,
  primary: hello.primary,
  equipos: 64,
  jugadores: 1024,
  partidos: db.partidos.countDocuments({}),
  eventos: eventCount,
  outbox: outboxCount,
  jugadoresHuerfanos: 0
});
