// ======================================================
// Fixture 2030 - Hito 4
// Análisis de rendimiento e índices
// ======================================================

db = db.getSiblingDB("fixture2030");


// ======================================================
// 1. ELIMINAR ÍNDICE SI YA EXISTE
// Permite ejecutar nuevamente el script y reproducir
// correctamente la comparación antes/después.
// ======================================================

const indices = db.jugadores.getIndexes();

if (indices.some(indice => indice.name === "idx_jugadores_equipo")) {
  db.jugadores.dropIndex("idx_jugadores_equipo");
  print("Índice previo eliminado.");
}


// ======================================================
// 2. CONSULTA ANTES DEL ÍNDICE
// Se buscan los jugadores del equipo EQ-01.
// Sin índice, MongoDB debe recorrer la colección.
// ======================================================

print("\n=== ANTES DEL ÍNDICE ===");

const antes = db.jugadores
  .find({ equipo_id: "EQ-01" })
  .explain("executionStats");

print("stage:", antes.queryPlanner.winningPlan.stage);
print("nReturned:", antes.executionStats.nReturned);
print("totalKeysExamined:", antes.executionStats.totalKeysExamined);
print("totalDocsExamined:", antes.executionStats.totalDocsExamined);
print("executionTimeMillis:", antes.executionStats.executionTimeMillis);


// ======================================================
// 3. CREACIÓN DEL ÍNDICE
// Se crea un índice sobre equipo_id porque es un campo
// utilizado frecuentemente para recuperar los jugadores
// pertenecientes a un equipo.
// ======================================================

print("\n=== CREACIÓN DEL ÍNDICE ===");

db.jugadores.createIndex(
  { equipo_id: 1 },
  { name: "idx_jugadores_equipo" }
);

print("Índice idx_jugadores_equipo creado.");


// ======================================================
// 4. CONSULTA DESPUÉS DEL ÍNDICE
// Se repite exactamente la misma consulta para comparar
// el plan de ejecución y la cantidad de documentos leídos.
// ======================================================

print("\n=== DESPUÉS DEL ÍNDICE ===");

const despues = db.jugadores
  .find({ equipo_id: "EQ-01" })
  .explain("executionStats");

print("stagePrincipal:", despues.queryPlanner.winningPlan.stage);
print("stageIndice:", despues.queryPlanner.winningPlan.inputStage.stage);
print("indiceUtilizado:", despues.queryPlanner.winningPlan.inputStage.indexName);
print("nReturned:", despues.executionStats.nReturned);
print("totalKeysExamined:", despues.executionStats.totalKeysExamined);
print("totalDocsExamined:", despues.executionStats.totalDocsExamined);
print("executionTimeMillis:", despues.executionStats.executionTimeMillis);


// ======================================================
// 5. LISTADO FINAL DE ÍNDICES
// Permite verificar que el índice quedó creado.
// ======================================================

print("\n=== ÍNDICES DE LA COLECCIÓN JUGADORES ===");

db.jugadores.getIndexes().forEach(indice => {
  printjson(indice);
});


// ======================================================
// FIN
// ======================================================

print("\nAnálisis de rendimiento finalizado correctamente.");