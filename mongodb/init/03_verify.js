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
assertEqual(db.partidos.countDocuments({}), 1, "cantidad de partidos de demostración");
assertEqual(db.eventos_oficiales.countDocuments({}), 0, "eventos iniciales");
assertEqual(db.outbox.countDocuments({}), 0, "outbox inicial");

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
  partidos: 1,
  jugadoresHuerfanos: 0
});
