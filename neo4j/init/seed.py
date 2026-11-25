import argparse
import json
import os
from pathlib import Path

from neo4j import GraphDatabase


CATALOG_ROOT = Path(os.getenv("CATALOG_ROOT", "/opt/fixture2030/catalogo"))
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD_FILE = Path(
    os.getenv("NEO4J_PASSWORD_FILE", ".secretos/neo4j-password.txt")
)
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def read_json(name):
    return json.loads((CATALOG_ROOT / name).read_text(encoding="utf-8"))


def run(session, query, **parameters):
    return session.run(query, **parameters).consume()


def apply_constraints(session):
    statements = (
        "CREATE CONSTRAINT fixture2030_equipo_id IF NOT EXISTS FOR (n:Equipo) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT fixture2030_jugador_id IF NOT EXISTS FOR (n:Jugador) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT fixture2030_partido_id IF NOT EXISTS FOR (n:Partido) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT fixture2030_confederacion_id IF NOT EXISTS FOR (n:Confederacion) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT fixture2030_torneo_id IF NOT EXISTS FOR (n:Torneo) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT fixture2030_demo_id IF NOT EXISTS FOR (n:NodoDemo) REQUIRE n.id IS UNIQUE",
        "CREATE INDEX fixture2030_jugador_posicion IF NOT EXISTS FOR (n:Jugador) ON (n.posicion)",
        "CREATE INDEX fixture2030_equipo_ranking IF NOT EXISTS FOR (n:Equipo) ON (n.ranking)",
    )
    for statement in statements:
        run(session, statement)


def seed_catalog(session, equipos, jugadores, partidos):
    confederaciones = sorted({equipo["confederacion"] for equipo in equipos})
    run(
        session,
        """
        MERGE (t:Torneo {id: 'TOR-2030'})
        SET t.nombre = 'Fixture 2030', t.anio = 2030
        """,
    )
    run(
        session,
        """
        UNWIND $ids AS id
        MERGE (c:Confederacion {id: id})
        SET c.nombre = id
        WITH c
        MATCH (t:Torneo {id: 'TOR-2030'})
        MERGE (c)-[:PARTICIPA_EN]->(t)
        """,
        ids=confederaciones,
    )
    run(
        session,
        """
        UNWIND $rows AS row
        MERGE (e:Equipo {id: row._id})
        SET e.nombre = row.nombre,
            e.confederacion = row.confederacion,
            e.ranking = row.ranking
        WITH e, row
        MATCH (c:Confederacion {id: row.confederacion})
        OPTIONAL MATCH (e)-[old:MIEMBRO_DE]->(:Confederacion)
        FOREACH (rel IN CASE WHEN old IS NULL THEN [] ELSE [old] END | DELETE rel)
        MERGE (e)-[:MIEMBRO_DE]->(c)
        """,
        rows=equipos,
    )
    run(
        session,
        """
        UNWIND $rows AS row
        MERGE (j:Jugador {id: row._id})
        SET j.nombre = row.nombre,
            j.fechaNacimiento = row.fecha_nacimiento,
            j.posicion = row.posicion
        WITH j, row
        MATCH (e:Equipo {id: row.equipo_id})
        OPTIONAL MATCH (j)-[old:PERTENECE_A]->(:Equipo)
        FOREACH (rel IN CASE WHEN old IS NULL THEN [] ELSE [old] END | DELETE rel)
        MERGE (j)-[:PERTENECE_A]->(e)
        """,
        rows=jugadores,
    )
    run(
        session,
        """
        UNWIND $rows AS row
        MERGE (p:Partido {id: row._id})
        SET p.inicioProgramado = row.inicio_programado,
            p.estado = row.estado,
            p.alcance = row.alcance
        WITH p, row
        OPTIONAL MATCH (:Equipo)-[old:LOCAL_EN|VISITANTE_EN]->(p)
        FOREACH (rel IN CASE WHEN old IS NULL THEN [] ELSE [old] END | DELETE rel)
        WITH p, row
        MATCH (local:Equipo {id: row.equipo_local_id})
        MATCH (visitante:Equipo {id: row.equipo_visitante_id})
        MATCH (t:Torneo {id: 'TOR-2030'})
        MERGE (local)-[:LOCAL_EN]->(p)
        MERGE (visitante)-[:VISITANTE_EN]->(p)
        MERGE (p)-[:FORMA_PARTE_DE]->(t)
        """,
        rows=partidos,
    )
    return len(confederaciones)


def verify(session, expected_confederations):
    query = """
    MATCH (e:Equipo) WITH count(e) AS equipos
    MATCH (j:Jugador) WITH equipos, count(j) AS jugadores
    MATCH (p:Partido) WITH equipos, jugadores, count(p) AS partidos
    MATCH (c:Confederacion) WITH equipos, jugadores, partidos, count(c) AS confederaciones
    MATCH (t:Torneo) WITH equipos, jugadores, partidos, confederaciones, count(t) AS torneos
    OPTIONAL MATCH (orphan:Jugador)
    WHERE NOT (orphan)-[:PERTENECE_A]->(:Equipo)
    RETURN equipos, jugadores, partidos, confederaciones, torneos,
           count(orphan) AS jugadoresHuerfanos
    """
    record = session.run(query).single(strict=True)
    result = dict(record)
    expected = {
        "equipos": 64,
        "jugadores": 1024,
        "partidos": 1,
        "confederaciones": expected_confederations,
        "torneos": 1,
        "jugadoresHuerfanos": 0,
    }
    if result != expected:
        raise RuntimeError(f"Verificacion Neo4j invalida: {result}; esperado: {expected}")
    constraints = session.run(
        "SHOW CONSTRAINTS YIELD name WHERE name STARTS WITH 'fixture2030_' RETURN count(*) AS total"
    ).single(strict=True)["total"]
    if constraints < 6:
        raise RuntimeError(f"Se esperaban al menos 6 restricciones; se encontraron {constraints}")
    result["restricciones"] = constraints
    return result


def demo_crud(session):
    run(session, "MATCH (n:NodoDemo {id: 'DEMO-CRUD'}) DETACH DELETE n")
    run(
        session,
        "CREATE (n:NodoDemo {id: 'DEMO-CRUD', nombre: 'Creado', estado: 'NUEVO'})",
    )
    run(
        session,
        "MATCH (n:NodoDemo {id: 'DEMO-CRUD'}) SET n.nombre = 'Actualizado', n.estado = 'VALIDADO'",
    )
    record = session.run(
        "MATCH (n:NodoDemo {id: 'DEMO-CRUD'}) RETURN n.nombre AS nombre, n.estado AS estado"
    ).single(strict=True)
    if dict(record) != {"nombre": "Actualizado", "estado": "VALIDADO"}:
        raise RuntimeError("La lectura posterior a la actualizacion CRUD no coincide")
    run(session, "MATCH (n:NodoDemo {id: 'DEMO-CRUD'}) DELETE n")
    remaining = session.run(
        "MATCH (n:NodoDemo {id: 'DEMO-CRUD'}) RETURN count(n) AS total"
    ).single(strict=True)["total"]
    if remaining != 0:
        raise RuntimeError("El nodo temporal de CRUD no fue eliminado")
    return {"create": "OK", "read": "OK", "update": "OK", "delete": "OK"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--demo-crud", action="store_true")
    args = parser.parse_args()
    if not any((args.seed, args.verify, args.demo_crud)):
        parser.error("Seleccione --seed, --verify o --demo-crud")

    password = NEO4J_PASSWORD_FILE.read_text(encoding="utf-8").strip()
    equipos = read_json("equipos.json")
    jugadores = read_json("jugadores.json")
    partidos = read_json("partidos.json")
    expected_confederations = len({item["confederacion"] for item in equipos})

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, password),
        connection_timeout=10,
    )
    try:
        driver.verify_connectivity()
        with driver.session(database=NEO4J_DATABASE) as session:
            if args.seed:
                apply_constraints(session)
                seed_catalog(session, equipos, jugadores, partidos)
            if args.demo_crud:
                print(json.dumps(demo_crud(session), ensure_ascii=False))
            else:
                print(json.dumps(verify(session, expected_confederations), ensure_ascii=False))
    finally:
        driver.close()


if __name__ == "__main__":
    main()
