"""Limpieza recuperable del historial de simulaciones; se ejecuta por CLI."""

import argparse
import json
from datetime import datetime, timezone
from uuid import uuid4

from pymongo import ReadPreference, ReturnDocument
from pymongo.errors import CollectionInvalid
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from .config import settings
from .database import get_client

ARCHIVE = "simulaciones_archivadas"
INACTIVE = ["LISTA", "FINALIZADA", "ERROR"]


def cleanup_history(client, cutoff, apply=False, batch_id=None):
    db = client.get_database(settings.mongodb_database)
    filters = {"estado": {"$in": INACTIVE}, "creadoEn": {"$lte": cutoff}}
    ids = [row["_id"] for row in db.simulaciones.find(filters, {"_id": 1})]
    result = {"loteId": batch_id or f"LIM-{uuid4()}", "candidatas": len(ids),
              "eliminadas": [], "preservadasPorCambioDeEstado": [], "aplicado": apply}
    if not apply or not ids:
        return result
    try:
        db.create_collection(ARCHIVE)
    except CollectionInvalid:
        pass
    archive = db[ARCHIVE]
    for simulation_id in ids:
        def transaction(session):
            # Releer dentro de la transacción protege un partido iniciado durante la limpieza.
            doc = db.simulaciones.find_one({**filters, "_id": simulation_id}, session=session)
            if doc is None:
                return None
            archive.insert_one({
                "_id": f"{result['loteId']}:{simulation_id}", "loteId": result["loteId"],
                "archivadaEn": cutoff, "simulacion": doc,
            }, session=session)
            deleted = db.simulaciones.delete_one({"_id": simulation_id, "estado": doc["estado"]}, session=session)
            if deleted.deleted_count != 1:
                raise RuntimeError("La simulación cambió antes de completar su respaldo")
            return simulation_id
        with client.start_session() as session:
            removed = session.with_transaction(
                transaction, read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", wtimeout=5000),
                read_preference=ReadPreference.PRIMARY,
            )
        result["eliminadas" if removed else "preservadasPorCambioDeEstado"].append(simulation_id)
    return result


def restore_history(client, batch_id):
    if not batch_id.startswith("LIM-") or len(batch_id) != 40:
        raise ValueError("Identificador de lote inválido")
    db = client.get_database(settings.mongodb_database)
    restored = 0
    for row in db[ARCHIVE].find({"loteId": batch_id}):
        document = row["simulacion"]
        # Repetir la restauración no reinicia ni pisa una simulación ya existente.
        result = db.simulaciones.update_one({"_id": document["_id"]}, {"$setOnInsert": document}, upsert=True)
        restored += result.upserted_id is not None
    return {"loteId": batch_id, "restauradas": restored}


def apply_update_cleanup(client, now):
    """La misma actualización no debe borrar los partidos nuevos al volver a aplicarla."""
    db = client.get_database(settings.mongodb_database)
    job = db.mantenimientos.find_one_and_update(
        {"_id": "limpieza-incremento-14"},
        {"$setOnInsert": {"corte": now, "loteId": f"LIM-{uuid4()}", "completada": False}},
        upsert=True, return_document=ReturnDocument.AFTER,
    )
    if job.get("completada"):
        return {"loteId": job["loteId"], "aplicado": False, "motivo": "Esta limpieza ya fue aplicada; se conservan los partidos nuevos."}
    print(json.dumps({"loteId": job["loteId"], "respaldo": ARCHIVE}), flush=True)
    result = cleanup_history(client, job["corte"], True, job["loteId"])
    db.mantenimientos.update_one(
        {"_id": job["_id"], "loteId": job["loteId"]},
        {"$set": {"completada": True, "completadaEn": now}},
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--restore", metavar="LOTE_ID")
    args = parser.parse_args()
    if args.restore and args.apply:
        parser.error("Elegí limpiar o restaurar")
    client = get_client()
    now = datetime.now(timezone.utc)
    result = restore_history(client, args.restore) if args.restore else (
        apply_update_cleanup(client, now) if args.apply else cleanup_history(client, now)
    )
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
