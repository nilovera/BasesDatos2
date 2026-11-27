db = db.getSiblingDB("fixture2030");
// Cola transaccional de entrega, no autoridad del historial de auditoria.
if (!db.getCollectionNames().includes("auditoria_pendiente")) {
  db.createCollection("auditoria_pendiente");
}
db.auditoria_pendiente.createIndex({ estado: 1, proximoIntentoEn: 1, creadoEn: 1 });
db.auditoria_pendiente.createIndex({ estado: 1, bloqueoHasta: 1 });
print("Cola durable de auditoria preparada sin modificar datos existentes.");
