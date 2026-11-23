/* global db */

// Fixture 2030 - esquema MongoDB inicial.
// Ejecutar con mongosh. Es idempotente respecto de colecciones e índices.

db = db.getSiblingDB("fixture2030");

const idPatterns = {
  equipo: "^EQ-[0-9]{2}$",
  jugador: "^JUG-[0-9]{4}$",
  partido: "^PAR-[0-9]{4}$",
  evento: "^EVE-[0-9]{6}$"
};

function ensureCollection(name, validator) {
  const options = {
    validator,
    validationLevel: "strict",
    validationAction: "error"
  };

  if (db.getCollectionNames().includes(name)) {
    db.runCommand({ collMod: name, ...options });
  } else {
    db.createCollection(name, options);
  }
}

ensureCollection("equipos", {
  $jsonSchema: {
    bsonType: "object",
    additionalProperties: false,
    required: [
      "_id", "equipoId", "nombre", "confederacion", "ranking",
      "activo", "creadoEn", "actualizadoEn"
    ],
    properties: {
      _id: { bsonType: "string", pattern: idPatterns.equipo },
      equipoId: { bsonType: "string", pattern: idPatterns.equipo },
      nombre: { bsonType: "string", minLength: 1, maxLength: 120 },
      confederacion: { bsonType: "string", minLength: 2, maxLength: 20 },
      ranking: { bsonType: "int", minimum: 1 },
      codigoExterno: { bsonType: "string", pattern: "^[A-Z]{3}$" },
      activo: { bsonType: "bool" },
      creadoEn: { bsonType: "date" },
      actualizadoEn: { bsonType: "date" }
    }
  }
});

ensureCollection("jugadores", {
  $jsonSchema: {
    bsonType: "object",
    additionalProperties: false,
    required: [
      "_id", "jugadorId", "equipoId", "nombre", "posicion",
      "fechaNacimiento", "activo", "creadoEn", "actualizadoEn"
    ],
    properties: {
      _id: { bsonType: "string", pattern: idPatterns.jugador },
      jugadorId: { bsonType: "string", pattern: idPatterns.jugador },
      equipoId: { bsonType: "string", pattern: idPatterns.equipo },
      nombre: { bsonType: "string", minLength: 1, maxLength: 160 },
      posicion: { enum: ["ARQUERO", "DEFENSOR", "MEDIOCAMPISTA", "DELANTERO"] },
      fechaNacimiento: { bsonType: "date" },
      activo: { bsonType: "bool" },
      creadoEn: { bsonType: "date" },
      actualizadoEn: { bsonType: "date" }
    }
  }
});

const lineupSchema = {
  bsonType: "object",
  additionalProperties: false,
  required: ["titulares", "suplentes"],
  properties: {
    titulares: {
      bsonType: "array",
      maxItems: 11,
      uniqueItems: true,
      items: { bsonType: "string", pattern: idPatterns.jugador }
    },
    suplentes: {
      bsonType: "array",
      maxItems: 15,
      uniqueItems: true,
      items: { bsonType: "string", pattern: idPatterns.jugador }
    }
  }
};

ensureCollection("partidos", {
  $and: [
    {
      $jsonSchema: {
        bsonType: "object",
        additionalProperties: false,
        required: [
          "_id", "partidoId", "equipos", "inicioProgramado", "estado",
          "marcador", "alineaciones", "ultimaSecuencia", "version",
          "creadoEn", "actualizadoEn"
        ],
        properties: {
          _id: { bsonType: "string", pattern: idPatterns.partido },
          partidoId: { bsonType: "string", pattern: idPatterns.partido },
          equipos: {
            bsonType: "object",
            additionalProperties: false,
            required: ["localId", "visitanteId"],
            properties: {
              localId: { bsonType: "string", pattern: idPatterns.equipo },
              visitanteId: { bsonType: "string", pattern: idPatterns.equipo }
            }
          },
          inicioProgramado: { bsonType: "date" },
          inicioReal: { bsonType: ["date", "null"] },
          finReal: { bsonType: ["date", "null"] },
          estado: { enum: ["PROGRAMADO", "EN_CURSO", "SUSPENDIDO", "FINALIZADO", "CANCELADO"] },
          marcador: {
            bsonType: "object",
            additionalProperties: false,
            required: ["local", "visitante"],
            properties: {
              local: { bsonType: "int", minimum: 0 },
              visitante: { bsonType: "int", minimum: 0 }
            }
          },
          alineaciones: {
            bsonType: "object",
            additionalProperties: false,
            required: ["local", "visitante"],
            properties: { local: lineupSchema, visitante: lineupSchema }
          },
          ultimaSecuencia: { bsonType: "long", minimum: 0 },
          version: { bsonType: "long", minimum: 1 },
          creadoEn: { bsonType: "date" },
          actualizadoEn: { bsonType: "date" }
        }
      }
    },
    { $expr: { $ne: ["$equipos.localId", "$equipos.visitanteId"] } }
  ]
});

ensureCollection("eventos_oficiales", {
  $jsonSchema: {
    bsonType: "object",
    additionalProperties: false,
    required: [
      "_id", "eventoId", "partidoId", "secuencia", "tipo", "datos",
      "idempotencia", "ocurridoEn", "recibidoEn", "versionContrato", "respuestaHttp"
    ],
    properties: {
      _id: { bsonType: "string", pattern: idPatterns.evento },
      eventoId: { bsonType: "string", pattern: idPatterns.evento },
      partidoId: { bsonType: "string", pattern: idPatterns.partido },
      secuencia: { bsonType: "long", minimum: 1 },
      tipo: { enum: ["INICIO_PARTIDO", "GOL", "SUSTITUCION", "CORRECCION_EVENTO"] },
      datos: { bsonType: "object" },
      referencia: {
        bsonType: "object",
        additionalProperties: false,
        properties: {
          eventoOriginalId: { bsonType: "string", pattern: idPatterns.evento }
        }
      },
      idempotencia: {
        bsonType: "object",
        additionalProperties: false,
        required: ["clave", "hashSolicitud"],
        properties: {
          clave: { bsonType: "string", minLength: 16, maxLength: 128 },
          hashSolicitud: { bsonType: "string", pattern: "^[a-f0-9]{64}$" }
        }
      },
      ocurridoEn: { bsonType: "date" },
      recibidoEn: { bsonType: "date" },
      versionContrato: { bsonType: "int", minimum: 1 },
      respuestaHttp: {
        bsonType: "object",
        additionalProperties: false,
        required: ["status", "body"],
        properties: {
          status: { bsonType: "int", minimum: 200, maximum: 299 },
          body: { bsonType: "object" }
        }
      }
    }
  }
});

ensureCollection("outbox", {
  $jsonSchema: {
    bsonType: "object",
    additionalProperties: false,
    required: [
      "_id", "outboxId", "eventoId", "partidoId", "tipo", "secuencia",
      "payload", "versionContrato", "estado", "intentos", "creadoEn", "actualizadoEn"
    ],
    properties: {
      _id: { bsonType: "string", minLength: 1, maxLength: 128 },
      outboxId: { bsonType: "string", minLength: 1, maxLength: 128 },
      eventoId: { bsonType: "string", pattern: idPatterns.evento },
      partidoId: { bsonType: "string", pattern: idPatterns.partido },
      tipo: { enum: ["INICIO_PARTIDO", "GOL", "SUSTITUCION", "CORRECCION_EVENTO"] },
      secuencia: { bsonType: "long", minimum: 1 },
      payload: { bsonType: "object" },
      versionContrato: { bsonType: "int", minimum: 1 },
      estado: { enum: ["PENDIENTE", "PROCESANDO", "PUBLICADO", "FALLIDO"] },
      intentos: { bsonType: "int", minimum: 0 },
      proximoIntentoEn: { bsonType: ["date", "null"] },
      ultimoError: { bsonType: ["string", "null"], maxLength: 500 },
      bloqueo: {
        bsonType: "object",
        additionalProperties: false,
        properties: {
          workerId: { bsonType: "string", maxLength: 120 },
          hasta: { bsonType: "date" }
        }
      },
      creadoEn: { bsonType: "date" },
      actualizadoEn: { bsonType: "date" },
      publicadoEn: { bsonType: ["date", "null"] },
      expiraEn: { bsonType: ["date", "null"] }
    }
  }
});

ensureCollection("contadores", {
  $jsonSchema: {
    bsonType: "object",
    additionalProperties: false,
    required: ["_id", "valor"],
    properties: {
      _id: { enum: ["eventos"] },
      valor: { bsonType: ["int", "long"], minimum: 0 }
    }
  }
});

db.equipos.createIndex({ equipoId: 1 }, { unique: true, name: "uq_equipos_equipoId" });
db.equipos.createIndex(
  { codigoExterno: 1 },
  {
    unique: true,
    name: "uq_equipos_codigoExterno",
    partialFilterExpression: { codigoExterno: { $type: "string" } }
  }
);

db.jugadores.createIndex({ jugadorId: 1 }, { unique: true, name: "uq_jugadores_jugadorId" });
db.jugadores.createIndex(
  { equipoId: 1, activo: 1, jugadorId: 1 },
  { name: "ix_jugadores_equipo_activo" }
);

db.partidos.createIndex({ partidoId: 1 }, { unique: true, name: "uq_partidos_partidoId" });
db.partidos.createIndex(
  { estado: 1, inicioProgramado: 1, partidoId: 1 },
  { name: "ix_partidos_estado_inicio" }
);
db.partidos.createIndex(
  { "equipos.localId": 1, inicioProgramado: 1 },
  { name: "ix_partidos_local_inicio" }
);
db.partidos.createIndex(
  { "equipos.visitanteId": 1, inicioProgramado: 1 },
  { name: "ix_partidos_visitante_inicio" }
);

db.eventos_oficiales.createIndex(
  { eventoId: 1 },
  { unique: true, name: "uq_eventos_eventoId" }
);
db.eventos_oficiales.createIndex(
  { partidoId: 1, secuencia: 1 },
  { unique: true, name: "uq_eventos_partido_secuencia" }
);
db.eventos_oficiales.createIndex(
  { "idempotencia.clave": 1 },
  { unique: true, name: "uq_eventos_idempotencia" }
);
db.eventos_oficiales.createIndex(
  { partidoId: 1, recibidoEn: 1, eventoId: 1 },
  { name: "ix_eventos_partido_recepcion" }
);
db.eventos_oficiales.createIndex(
  { "referencia.eventoOriginalId": 1 },
  {
    name: "ix_eventos_original",
    partialFilterExpression: { "referencia.eventoOriginalId": { $type: "string" } }
  }
);

db.outbox.createIndex({ outboxId: 1 }, { unique: true, name: "uq_outbox_outboxId" });
db.outbox.createIndex({ eventoId: 1 }, { unique: true, name: "uq_outbox_eventoId" });
db.outbox.createIndex(
  { estado: 1, proximoIntentoEn: 1, creadoEn: 1 },
  { name: "ix_outbox_pendientes" }
);
db.outbox.createIndex(
  { "bloqueo.hasta": 1 },
  {
    name: "ix_outbox_bloqueo",
    partialFilterExpression: { "bloqueo.hasta": { $type: "date" } }
  }
);
db.outbox.createIndex(
  { expiraEn: 1 },
  {
    name: "ttl_outbox_publicada",
    expireAfterSeconds: 0,
    partialFilterExpression: { estado: "PUBLICADO", expiraEn: { $type: "date" } }
  }
);

print("Esquema e índices de fixture2030 aplicados correctamente.");
