/* global db, rs, sleep */

// Inicializa una sola vez el replica set de laboratorio y espera el PRIMARY.
// El hostname debe coincidir con el servicio definido en docker-compose.yml.

try {
  rs.status();
  print("Replica set rs0 ya estaba inicializado.");
} catch (error) {
  if (error.code === 94 || error.codeName === "NotYetInitialized") {
    rs.initiate({
      _id: "rs0",
      members: [{ _id: 0, host: "mongo:27017" }]
    });
    print("Inicialización de rs0 solicitada.");
  } else {
    throw error;
  }
}

let primaryReady = false;
for (let attempt = 1; attempt <= 60; attempt += 1) {
  const hello = db.getSiblingDB("admin").runCommand({ hello: 1 });
  if (hello.isWritablePrimary === true) {
    primaryReady = true;
    print(`rs0 PRIMARY disponible después de ${attempt} intento(s).`);
    break;
  }
  sleep(1000);
}

if (!primaryReady) {
  throw new Error("rs0 no eligió un PRIMARY dentro de 60 segundos");
}
