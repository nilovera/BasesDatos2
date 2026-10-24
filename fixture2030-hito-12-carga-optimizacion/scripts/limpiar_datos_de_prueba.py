"""LIMPIEZA OPCIONAL: borra SOLO los datos sintéticos creados por preparar_datos.py.

  - Redis: claves sesion:SES-H12-*
  - IRIS : partidos PAR-H12* y sus eventos
  - Cassandra: los comentarios sintéticos H12 (se recalculan sus claves exactas; no se toca nada más)
No toca datos de otros hitos ni borra la evidencia (docs/evidencia) ni el catálogo.
Requiere confirmar con --confirmar para evitar borrados accidentales.

Uso:  python limpiar_datos_de_prueba.py --confirmar
"""
from __future__ import annotations

import sys

import comun


def main() -> int:
    if "--confirmar" not in sys.argv:
        print(__doc__)
        return 1
    s = comun.get_settings()
    import redis
    c = redis.Redis(host=s.redis_host, port=s.redis_port, db=s.redis_database)
    claves = list(c.scan_iter(match=f"sesion:{comun.PREFIJO_SESION_REDIS}*", count=500))
    borradas = c.delete(*claves) if claves else 0
    c.close()
    print(f"Redis: {borradas} sesiones SES-H12-* eliminadas")

    import iris.dbapi as iris_dbapi
    con = iris_dbapi.connect(s.iris_host, s.iris_port, s.iris_namespace, s.iris_username,
                             s.iris_password.get_secret_value())
    cur = con.cursor()
    pref = comun.PREFIJO_PARTIDO_IRIS
    cur.execute("DELETE FROM Fixture.EventoPartido WHERE Partido->Codigo %STARTSWITH ?", [pref])
    cur.execute("DELETE FROM Fixture.Partido WHERE Codigo %STARTSWITH ?", [pref])
    try:
        con.commit()
    except Exception:  # noqa: BLE001
        pass
    cur.execute("SELECT COUNT(*) FROM Fixture.Partido WHERE Codigo %STARTSWITH ?", [pref])
    print(f"IRIS: partidos {pref}* restantes = {cur.fetchall()[0][0]}")
    cur.close()
    con.close()
    from cassandra.concurrent import execute_concurrent_with_args
    cfg = comun.cargar_config()
    cluster, ses = comun.sesion_cassandra()
    del_p = ses.prepare("DELETE FROM comentarios_por_partido WHERE partido_id=? AND bucket_10min=? AND creado_en=? AND comentario_id=?")
    del_u = ses.prepare("DELETE FROM comentarios_por_usuario WHERE usuario_id=? AND bucket_dia=? AND creado_en=? AND comentario_id=?")
    com = list(comun.comentarios_sinteticos(cfg["datos_sinteticos"]["comentarios_por_bucket_cassandra"], cfg["semilla"]))
    execute_concurrent_with_args(ses, del_p, [(c["partido_id"], c["bucket_10min"], c["creado_en"], c["comentario_id"]) for c in com], concurrency=64)
    execute_concurrent_with_args(ses, del_u, [(c["usuario_id"], c["bucket_dia"], c["creado_en"], c["comentario_id"]) for c in com], concurrency=64)
    cluster.shutdown()
    print(f"Cassandra: {len(com)} comentarios sintéticos eliminados de las 2 tablas")
    print("Listo. Para volver a probar: preparar_datos.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
