// ======================================================
// Fixture 2030 - Hito 5
// Segunda carga: Sedes, Partidos, Eventos y relaciones
// Ejecutar después de carga.cypher
// ======================================================

// 1. CARGA DE 16 SEDES

MERGE (s:Sede {codigo: 'SED-01'})
SET s.nombre = 'Buenos Aires';

MERGE (s:Sede {codigo: 'SED-02'})
SET s.nombre = 'Montevideo';

MERGE (s:Sede {codigo: 'SED-03'})
SET s.nombre = 'Asunción';

MERGE (s:Sede {codigo: 'SED-04'})
SET s.nombre = 'Madrid';

MERGE (s:Sede {codigo: 'SED-05'})
SET s.nombre = 'Barcelona';

MERGE (s:Sede {codigo: 'SED-06'})
SET s.nombre = 'Sevilla';

MERGE (s:Sede {codigo: 'SED-07'})
SET s.nombre = 'Bilbao';

MERGE (s:Sede {codigo: 'SED-08'})
SET s.nombre = 'Valencia';

MERGE (s:Sede {codigo: 'SED-09'})
SET s.nombre = 'San Sebastián';

MERGE (s:Sede {codigo: 'SED-10'})
SET s.nombre = 'Zaragoza';

MERGE (s:Sede {codigo: 'SED-11'})
SET s.nombre = 'Lisboa';

MERGE (s:Sede {codigo: 'SED-12'})
SET s.nombre = 'Oporto';

MERGE (s:Sede {codigo: 'SED-13'})
SET s.nombre = 'Casablanca';

MERGE (s:Sede {codigo: 'SED-14'})
SET s.nombre = 'Rabat';

MERGE (s:Sede {codigo: 'SED-15'})
SET s.nombre = 'Marrakech';

MERGE (s:Sede {codigo: 'SED-16'})
SET s.nombre = 'Tánger';

// 2. CARGA DE 96 PARTIDOS Y RELACIONES CON EQUIPOS Y SEDES

MERGE (p:Partido {codigo: 'PAR-0001'})
SET p.fecha = date('2030-06-13'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-01'})
MERGE (visitante:Equipo {codigo: 'EQ-17'})
MERGE (s:Sede {codigo: 'SED-01'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0001'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0001'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0002'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 26
MERGE (p:Partido {codigo: 'PAR-0001'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0002'})
SET p.fecha = date('2030-06-13'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-01'})
MERGE (visitante:Equipo {codigo: 'EQ-33'})
MERGE (s:Sede {codigo: 'SED-01'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0003'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0002'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0004'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 37
MERGE (p:Partido {codigo: 'PAR-0002'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0003'})
SET p.fecha = date('2030-06-13'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-01'})
MERGE (visitante:Equipo {codigo: 'EQ-49'})
MERGE (s:Sede {codigo: 'SED-01'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0005'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0003'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0006'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 48
MERGE (p:Partido {codigo: 'PAR-0003'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0004'})
SET p.fecha = date('2030-06-13'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-17'})
MERGE (visitante:Equipo {codigo: 'EQ-33'})
MERGE (s:Sede {codigo: 'SED-01'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0007'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0004'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0008'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0004'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0005'})
SET p.fecha = date('2030-06-14'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-17'})
MERGE (visitante:Equipo {codigo: 'EQ-49'})
MERGE (s:Sede {codigo: 'SED-01'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0009'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0005'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0010'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 70
MERGE (p:Partido {codigo: 'PAR-0005'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0006'})
SET p.fecha = date('2030-06-14'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-33'})
MERGE (visitante:Equipo {codigo: 'EQ-49'})
MERGE (s:Sede {codigo: 'SED-01'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0011'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0006'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0012'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 81
MERGE (p:Partido {codigo: 'PAR-0006'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0007'})
SET p.fecha = date('2030-06-14'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-02'})
MERGE (visitante:Equipo {codigo: 'EQ-18'})
MERGE (s:Sede {codigo: 'SED-02'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0013'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0007'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0014'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 22
MERGE (p:Partido {codigo: 'PAR-0007'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0008'})
SET p.fecha = date('2030-06-14'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-02'})
MERGE (visitante:Equipo {codigo: 'EQ-34'})
MERGE (s:Sede {codigo: 'SED-02'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0015'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0008'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0016'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 33
MERGE (p:Partido {codigo: 'PAR-0008'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0009'})
SET p.fecha = date('2030-06-15'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-02'})
MERGE (visitante:Equipo {codigo: 'EQ-50'})
MERGE (s:Sede {codigo: 'SED-02'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0017'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0009'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0018'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 44
MERGE (p:Partido {codigo: 'PAR-0009'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0010'})
SET p.fecha = date('2030-06-15'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-18'})
MERGE (visitante:Equipo {codigo: 'EQ-34'})
MERGE (s:Sede {codigo: 'SED-02'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0019'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0010'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0020'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 55
MERGE (p:Partido {codigo: 'PAR-0010'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0011'})
SET p.fecha = date('2030-06-15'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-18'})
MERGE (visitante:Equipo {codigo: 'EQ-50'})
MERGE (s:Sede {codigo: 'SED-02'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0021'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0011'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0022'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0011'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0012'})
SET p.fecha = date('2030-06-15'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-34'})
MERGE (visitante:Equipo {codigo: 'EQ-50'})
MERGE (s:Sede {codigo: 'SED-02'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0023'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0012'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0024'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 77
MERGE (p:Partido {codigo: 'PAR-0012'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0013'})
SET p.fecha = date('2030-06-16'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-03'})
MERGE (visitante:Equipo {codigo: 'EQ-19'})
MERGE (s:Sede {codigo: 'SED-03'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0025'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0013'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0026'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 18
MERGE (p:Partido {codigo: 'PAR-0013'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0014'})
SET p.fecha = date('2030-06-16'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-03'})
MERGE (visitante:Equipo {codigo: 'EQ-35'})
MERGE (s:Sede {codigo: 'SED-03'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0027'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0014'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0028'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 29
MERGE (p:Partido {codigo: 'PAR-0014'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0015'})
SET p.fecha = date('2030-06-16'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-03'})
MERGE (visitante:Equipo {codigo: 'EQ-51'})
MERGE (s:Sede {codigo: 'SED-03'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0029'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0015'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0030'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 40
MERGE (p:Partido {codigo: 'PAR-0015'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0016'})
SET p.fecha = date('2030-06-16'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-19'})
MERGE (visitante:Equipo {codigo: 'EQ-35'})
MERGE (s:Sede {codigo: 'SED-03'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0031'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0016'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0032'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 51
MERGE (p:Partido {codigo: 'PAR-0016'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0017'})
SET p.fecha = date('2030-06-17'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-19'})
MERGE (visitante:Equipo {codigo: 'EQ-51'})
MERGE (s:Sede {codigo: 'SED-03'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0033'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0017'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0034'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 62
MERGE (p:Partido {codigo: 'PAR-0017'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0018'})
SET p.fecha = date('2030-06-17'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-35'})
MERGE (visitante:Equipo {codigo: 'EQ-51'})
MERGE (s:Sede {codigo: 'SED-03'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0035'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0018'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0036'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0018'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0019'})
SET p.fecha = date('2030-06-17'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-04'})
MERGE (visitante:Equipo {codigo: 'EQ-20'})
MERGE (s:Sede {codigo: 'SED-04'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0037'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0019'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0038'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 84
MERGE (p:Partido {codigo: 'PAR-0019'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0020'})
SET p.fecha = date('2030-06-17'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-04'})
MERGE (visitante:Equipo {codigo: 'EQ-36'})
MERGE (s:Sede {codigo: 'SED-04'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0039'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0020'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0040'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 25
MERGE (p:Partido {codigo: 'PAR-0020'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0021'})
SET p.fecha = date('2030-06-18'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-04'})
MERGE (visitante:Equipo {codigo: 'EQ-52'})
MERGE (s:Sede {codigo: 'SED-04'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0041'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0021'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0042'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 36
MERGE (p:Partido {codigo: 'PAR-0021'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0022'})
SET p.fecha = date('2030-06-18'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-20'})
MERGE (visitante:Equipo {codigo: 'EQ-36'})
MERGE (s:Sede {codigo: 'SED-04'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0043'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0022'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0044'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 47
MERGE (p:Partido {codigo: 'PAR-0022'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0023'})
SET p.fecha = date('2030-06-18'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-20'})
MERGE (visitante:Equipo {codigo: 'EQ-52'})
MERGE (s:Sede {codigo: 'SED-04'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0045'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0023'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0046'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 58
MERGE (p:Partido {codigo: 'PAR-0023'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0024'})
SET p.fecha = date('2030-06-18'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-36'})
MERGE (visitante:Equipo {codigo: 'EQ-52'})
MERGE (s:Sede {codigo: 'SED-04'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0047'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0024'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0048'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 69
MERGE (p:Partido {codigo: 'PAR-0024'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0025'})
SET p.fecha = date('2030-06-19'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-05'})
MERGE (visitante:Equipo {codigo: 'EQ-21'})
MERGE (s:Sede {codigo: 'SED-05'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0049'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0025'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0050'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 80
MERGE (p:Partido {codigo: 'PAR-0025'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0026'})
SET p.fecha = date('2030-06-19'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-05'})
MERGE (visitante:Equipo {codigo: 'EQ-37'})
MERGE (s:Sede {codigo: 'SED-05'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0051'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0026'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0052'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 21
MERGE (p:Partido {codigo: 'PAR-0026'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0027'})
SET p.fecha = date('2030-06-19'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-05'})
MERGE (visitante:Equipo {codigo: 'EQ-53'})
MERGE (s:Sede {codigo: 'SED-05'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0053'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0027'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0054'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 32
MERGE (p:Partido {codigo: 'PAR-0027'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0028'})
SET p.fecha = date('2030-06-19'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-21'})
MERGE (visitante:Equipo {codigo: 'EQ-37'})
MERGE (s:Sede {codigo: 'SED-05'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0055'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0028'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0056'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 43
MERGE (p:Partido {codigo: 'PAR-0028'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0029'})
SET p.fecha = date('2030-06-20'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-21'})
MERGE (visitante:Equipo {codigo: 'EQ-53'})
MERGE (s:Sede {codigo: 'SED-05'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0057'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0029'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0058'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 54
MERGE (p:Partido {codigo: 'PAR-0029'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0030'})
SET p.fecha = date('2030-06-20'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-37'})
MERGE (visitante:Equipo {codigo: 'EQ-53'})
MERGE (s:Sede {codigo: 'SED-05'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0059'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0030'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0060'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 65
MERGE (p:Partido {codigo: 'PAR-0030'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0031'})
SET p.fecha = date('2030-06-20'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-06'})
MERGE (visitante:Equipo {codigo: 'EQ-22'})
MERGE (s:Sede {codigo: 'SED-06'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0061'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0031'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0062'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 76
MERGE (p:Partido {codigo: 'PAR-0031'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0032'})
SET p.fecha = date('2030-06-20'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-06'})
MERGE (visitante:Equipo {codigo: 'EQ-38'})
MERGE (s:Sede {codigo: 'SED-06'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0063'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0032'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0064'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0032'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0033'})
SET p.fecha = date('2030-06-21'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-06'})
MERGE (visitante:Equipo {codigo: 'EQ-54'})
MERGE (s:Sede {codigo: 'SED-06'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0065'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0033'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0066'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 28
MERGE (p:Partido {codigo: 'PAR-0033'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0034'})
SET p.fecha = date('2030-06-21'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-22'})
MERGE (visitante:Equipo {codigo: 'EQ-38'})
MERGE (s:Sede {codigo: 'SED-06'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0067'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0034'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0068'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 39
MERGE (p:Partido {codigo: 'PAR-0034'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0035'})
SET p.fecha = date('2030-06-21'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-22'})
MERGE (visitante:Equipo {codigo: 'EQ-54'})
MERGE (s:Sede {codigo: 'SED-06'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0069'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0035'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0070'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 50
MERGE (p:Partido {codigo: 'PAR-0035'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0036'})
SET p.fecha = date('2030-06-21'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-38'})
MERGE (visitante:Equipo {codigo: 'EQ-54'})
MERGE (s:Sede {codigo: 'SED-06'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0071'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0036'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0072'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 61
MERGE (p:Partido {codigo: 'PAR-0036'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0037'})
SET p.fecha = date('2030-06-22'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-07'})
MERGE (visitante:Equipo {codigo: 'EQ-23'})
MERGE (s:Sede {codigo: 'SED-07'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0073'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0037'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0074'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 72
MERGE (p:Partido {codigo: 'PAR-0037'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0038'})
SET p.fecha = date('2030-06-22'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-07'})
MERGE (visitante:Equipo {codigo: 'EQ-39'})
MERGE (s:Sede {codigo: 'SED-07'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0075'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0038'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0076'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 83
MERGE (p:Partido {codigo: 'PAR-0038'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0039'})
SET p.fecha = date('2030-06-22'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-07'})
MERGE (visitante:Equipo {codigo: 'EQ-55'})
MERGE (s:Sede {codigo: 'SED-07'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0077'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0039'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0078'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0039'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0040'})
SET p.fecha = date('2030-06-22'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-23'})
MERGE (visitante:Equipo {codigo: 'EQ-39'})
MERGE (s:Sede {codigo: 'SED-07'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0079'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0040'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0080'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 35
MERGE (p:Partido {codigo: 'PAR-0040'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0041'})
SET p.fecha = date('2030-06-23'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-23'})
MERGE (visitante:Equipo {codigo: 'EQ-55'})
MERGE (s:Sede {codigo: 'SED-07'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0081'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0041'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0082'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 46
MERGE (p:Partido {codigo: 'PAR-0041'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0042'})
SET p.fecha = date('2030-06-23'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-39'})
MERGE (visitante:Equipo {codigo: 'EQ-55'})
MERGE (s:Sede {codigo: 'SED-07'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0083'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0042'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0084'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 57
MERGE (p:Partido {codigo: 'PAR-0042'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0043'})
SET p.fecha = date('2030-06-23'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-08'})
MERGE (visitante:Equipo {codigo: 'EQ-24'})
MERGE (s:Sede {codigo: 'SED-08'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0085'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0043'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0086'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 68
MERGE (p:Partido {codigo: 'PAR-0043'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0044'})
SET p.fecha = date('2030-06-23'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-08'})
MERGE (visitante:Equipo {codigo: 'EQ-40'})
MERGE (s:Sede {codigo: 'SED-08'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0087'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0044'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0088'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 79
MERGE (p:Partido {codigo: 'PAR-0044'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0045'})
SET p.fecha = date('2030-06-24'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-08'})
MERGE (visitante:Equipo {codigo: 'EQ-56'})
MERGE (s:Sede {codigo: 'SED-08'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0089'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0045'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0090'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 20
MERGE (p:Partido {codigo: 'PAR-0045'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0046'})
SET p.fecha = date('2030-06-24'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-24'})
MERGE (visitante:Equipo {codigo: 'EQ-40'})
MERGE (s:Sede {codigo: 'SED-08'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0091'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0046'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0092'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0046'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0047'})
SET p.fecha = date('2030-06-24'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-24'})
MERGE (visitante:Equipo {codigo: 'EQ-56'})
MERGE (s:Sede {codigo: 'SED-08'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0093'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0047'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0094'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 42
MERGE (p:Partido {codigo: 'PAR-0047'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0048'})
SET p.fecha = date('2030-06-24'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-40'})
MERGE (visitante:Equipo {codigo: 'EQ-56'})
MERGE (s:Sede {codigo: 'SED-08'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0095'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0048'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0096'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 53
MERGE (p:Partido {codigo: 'PAR-0048'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0049'})
SET p.fecha = date('2030-06-25'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-09'})
MERGE (visitante:Equipo {codigo: 'EQ-25'})
MERGE (s:Sede {codigo: 'SED-09'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0097'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0049'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0098'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 64
MERGE (p:Partido {codigo: 'PAR-0049'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0050'})
SET p.fecha = date('2030-06-25'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-09'})
MERGE (visitante:Equipo {codigo: 'EQ-41'})
MERGE (s:Sede {codigo: 'SED-09'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0099'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0050'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0100'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 75
MERGE (p:Partido {codigo: 'PAR-0050'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0051'})
SET p.fecha = date('2030-06-25'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-09'})
MERGE (visitante:Equipo {codigo: 'EQ-57'})
MERGE (s:Sede {codigo: 'SED-09'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0101'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0051'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0102'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 16
MERGE (p:Partido {codigo: 'PAR-0051'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0052'})
SET p.fecha = date('2030-06-25'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-25'})
MERGE (visitante:Equipo {codigo: 'EQ-41'})
MERGE (s:Sede {codigo: 'SED-09'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0103'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0052'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0104'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 27
MERGE (p:Partido {codigo: 'PAR-0052'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0053'})
SET p.fecha = date('2030-06-26'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-25'})
MERGE (visitante:Equipo {codigo: 'EQ-57'})
MERGE (s:Sede {codigo: 'SED-09'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0105'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0053'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0106'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0053'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0054'})
SET p.fecha = date('2030-06-26'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-41'})
MERGE (visitante:Equipo {codigo: 'EQ-57'})
MERGE (s:Sede {codigo: 'SED-09'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0107'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0054'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0108'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 49
MERGE (p:Partido {codigo: 'PAR-0054'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0055'})
SET p.fecha = date('2030-06-26'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-10'})
MERGE (visitante:Equipo {codigo: 'EQ-26'})
MERGE (s:Sede {codigo: 'SED-10'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0109'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0055'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0110'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 60
MERGE (p:Partido {codigo: 'PAR-0055'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0056'})
SET p.fecha = date('2030-06-26'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-10'})
MERGE (visitante:Equipo {codigo: 'EQ-42'})
MERGE (s:Sede {codigo: 'SED-10'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0111'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0056'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0112'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 71
MERGE (p:Partido {codigo: 'PAR-0056'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0057'})
SET p.fecha = date('2030-06-27'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-10'})
MERGE (visitante:Equipo {codigo: 'EQ-58'})
MERGE (s:Sede {codigo: 'SED-10'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0113'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0057'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0114'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 82
MERGE (p:Partido {codigo: 'PAR-0057'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0058'})
SET p.fecha = date('2030-06-27'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-26'})
MERGE (visitante:Equipo {codigo: 'EQ-42'})
MERGE (s:Sede {codigo: 'SED-10'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0115'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0058'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0116'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 23
MERGE (p:Partido {codigo: 'PAR-0058'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0059'})
SET p.fecha = date('2030-06-27'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-26'})
MERGE (visitante:Equipo {codigo: 'EQ-58'})
MERGE (s:Sede {codigo: 'SED-10'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0117'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0059'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0118'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 34
MERGE (p:Partido {codigo: 'PAR-0059'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0060'})
SET p.fecha = date('2030-06-27'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-42'})
MERGE (visitante:Equipo {codigo: 'EQ-58'})
MERGE (s:Sede {codigo: 'SED-10'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0119'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0060'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0120'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0060'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0061'})
SET p.fecha = date('2030-06-28'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-11'})
MERGE (visitante:Equipo {codigo: 'EQ-27'})
MERGE (s:Sede {codigo: 'SED-11'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0121'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0061'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0122'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 56
MERGE (p:Partido {codigo: 'PAR-0061'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0062'})
SET p.fecha = date('2030-06-28'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-11'})
MERGE (visitante:Equipo {codigo: 'EQ-43'})
MERGE (s:Sede {codigo: 'SED-11'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0123'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0062'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0124'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 67
MERGE (p:Partido {codigo: 'PAR-0062'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0063'})
SET p.fecha = date('2030-06-28'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-11'})
MERGE (visitante:Equipo {codigo: 'EQ-59'})
MERGE (s:Sede {codigo: 'SED-11'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0125'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0063'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0126'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 78
MERGE (p:Partido {codigo: 'PAR-0063'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0064'})
SET p.fecha = date('2030-06-28'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-27'})
MERGE (visitante:Equipo {codigo: 'EQ-43'})
MERGE (s:Sede {codigo: 'SED-11'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0127'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0064'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0128'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 19
MERGE (p:Partido {codigo: 'PAR-0064'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0065'})
SET p.fecha = date('2030-06-29'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-27'})
MERGE (visitante:Equipo {codigo: 'EQ-59'})
MERGE (s:Sede {codigo: 'SED-11'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0129'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0065'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0130'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 30
MERGE (p:Partido {codigo: 'PAR-0065'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0066'})
SET p.fecha = date('2030-06-29'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-43'})
MERGE (visitante:Equipo {codigo: 'EQ-59'})
MERGE (s:Sede {codigo: 'SED-11'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0131'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0066'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0132'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 41
MERGE (p:Partido {codigo: 'PAR-0066'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0067'})
SET p.fecha = date('2030-06-29'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-12'})
MERGE (visitante:Equipo {codigo: 'EQ-28'})
MERGE (s:Sede {codigo: 'SED-12'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0133'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0067'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0134'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0067'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0068'})
SET p.fecha = date('2030-06-29'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-12'})
MERGE (visitante:Equipo {codigo: 'EQ-44'})
MERGE (s:Sede {codigo: 'SED-12'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0135'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0068'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0136'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 63
MERGE (p:Partido {codigo: 'PAR-0068'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0069'})
SET p.fecha = date('2030-06-30'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-12'})
MERGE (visitante:Equipo {codigo: 'EQ-60'})
MERGE (s:Sede {codigo: 'SED-12'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0137'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0069'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0138'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 74
MERGE (p:Partido {codigo: 'PAR-0069'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0070'})
SET p.fecha = date('2030-06-30'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-28'})
MERGE (visitante:Equipo {codigo: 'EQ-44'})
MERGE (s:Sede {codigo: 'SED-12'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0139'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0070'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0140'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 15
MERGE (p:Partido {codigo: 'PAR-0070'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0071'})
SET p.fecha = date('2030-06-30'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-28'})
MERGE (visitante:Equipo {codigo: 'EQ-60'})
MERGE (s:Sede {codigo: 'SED-12'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0141'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0071'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0142'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 26
MERGE (p:Partido {codigo: 'PAR-0071'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0072'})
SET p.fecha = date('2030-06-30'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-44'})
MERGE (visitante:Equipo {codigo: 'EQ-60'})
MERGE (s:Sede {codigo: 'SED-12'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0143'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0072'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0144'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 37
MERGE (p:Partido {codigo: 'PAR-0072'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0073'})
SET p.fecha = date('2030-07-01'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-13'})
MERGE (visitante:Equipo {codigo: 'EQ-29'})
MERGE (s:Sede {codigo: 'SED-13'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0145'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0073'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0146'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 48
MERGE (p:Partido {codigo: 'PAR-0073'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0074'})
SET p.fecha = date('2030-07-01'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-13'})
MERGE (visitante:Equipo {codigo: 'EQ-45'})
MERGE (s:Sede {codigo: 'SED-13'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0147'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0074'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0148'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0074'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0075'})
SET p.fecha = date('2030-07-01'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-13'})
MERGE (visitante:Equipo {codigo: 'EQ-61'})
MERGE (s:Sede {codigo: 'SED-13'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0149'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0075'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0150'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 70
MERGE (p:Partido {codigo: 'PAR-0075'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0076'})
SET p.fecha = date('2030-07-01'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-29'})
MERGE (visitante:Equipo {codigo: 'EQ-45'})
MERGE (s:Sede {codigo: 'SED-13'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0151'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0076'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0152'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 81
MERGE (p:Partido {codigo: 'PAR-0076'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0077'})
SET p.fecha = date('2030-07-02'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-29'})
MERGE (visitante:Equipo {codigo: 'EQ-61'})
MERGE (s:Sede {codigo: 'SED-13'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0153'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0077'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0154'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 22
MERGE (p:Partido {codigo: 'PAR-0077'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0078'})
SET p.fecha = date('2030-07-02'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-45'})
MERGE (visitante:Equipo {codigo: 'EQ-61'})
MERGE (s:Sede {codigo: 'SED-13'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0155'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0078'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0156'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 33
MERGE (p:Partido {codigo: 'PAR-0078'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0079'})
SET p.fecha = date('2030-07-02'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-14'})
MERGE (visitante:Equipo {codigo: 'EQ-30'})
MERGE (s:Sede {codigo: 'SED-14'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0157'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0079'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0158'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 44
MERGE (p:Partido {codigo: 'PAR-0079'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0080'})
SET p.fecha = date('2030-07-02'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-14'})
MERGE (visitante:Equipo {codigo: 'EQ-46'})
MERGE (s:Sede {codigo: 'SED-14'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0159'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0080'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0160'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 55
MERGE (p:Partido {codigo: 'PAR-0080'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0081'})
SET p.fecha = date('2030-07-03'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-14'})
MERGE (visitante:Equipo {codigo: 'EQ-62'})
MERGE (s:Sede {codigo: 'SED-14'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0161'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0081'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0162'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0081'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0082'})
SET p.fecha = date('2030-07-03'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-30'})
MERGE (visitante:Equipo {codigo: 'EQ-46'})
MERGE (s:Sede {codigo: 'SED-14'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0163'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0082'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0164'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 77
MERGE (p:Partido {codigo: 'PAR-0082'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0083'})
SET p.fecha = date('2030-07-03'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-30'})
MERGE (visitante:Equipo {codigo: 'EQ-62'})
MERGE (s:Sede {codigo: 'SED-14'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0165'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0083'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0166'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 18
MERGE (p:Partido {codigo: 'PAR-0083'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0084'})
SET p.fecha = date('2030-07-03'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-46'})
MERGE (visitante:Equipo {codigo: 'EQ-62'})
MERGE (s:Sede {codigo: 'SED-14'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0167'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0084'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0168'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 29
MERGE (p:Partido {codigo: 'PAR-0084'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0085'})
SET p.fecha = date('2030-07-04'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-15'})
MERGE (visitante:Equipo {codigo: 'EQ-31'})
MERGE (s:Sede {codigo: 'SED-15'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0169'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0085'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0170'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 40
MERGE (p:Partido {codigo: 'PAR-0085'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0086'})
SET p.fecha = date('2030-07-04'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-15'})
MERGE (visitante:Equipo {codigo: 'EQ-47'})
MERGE (s:Sede {codigo: 'SED-15'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0171'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0086'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0172'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 51
MERGE (p:Partido {codigo: 'PAR-0086'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0087'})
SET p.fecha = date('2030-07-04'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-15'})
MERGE (visitante:Equipo {codigo: 'EQ-63'})
MERGE (s:Sede {codigo: 'SED-15'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0173'})
SET ev.tipo = 'Gol',
    ev.minuto = 59
MERGE (p:Partido {codigo: 'PAR-0087'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0174'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 62
MERGE (p:Partido {codigo: 'PAR-0087'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0088'})
SET p.fecha = date('2030-07-04'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-31'})
MERGE (visitante:Equipo {codigo: 'EQ-47'})
MERGE (s:Sede {codigo: 'SED-15'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0175'})
SET ev.tipo = 'Gol',
    ev.minuto = 66
MERGE (p:Partido {codigo: 'PAR-0088'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0176'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0088'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0089'})
SET p.fecha = date('2030-07-05'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-31'})
MERGE (visitante:Equipo {codigo: 'EQ-63'})
MERGE (s:Sede {codigo: 'SED-15'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0177'})
SET ev.tipo = 'Gol',
    ev.minuto = 73
MERGE (p:Partido {codigo: 'PAR-0089'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0178'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 84
MERGE (p:Partido {codigo: 'PAR-0089'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0090'})
SET p.fecha = date('2030-07-05'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-47'})
MERGE (visitante:Equipo {codigo: 'EQ-63'})
MERGE (s:Sede {codigo: 'SED-15'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0179'})
SET ev.tipo = 'Gol',
    ev.minuto = 10
MERGE (p:Partido {codigo: 'PAR-0090'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0180'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 25
MERGE (p:Partido {codigo: 'PAR-0090'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0091'})
SET p.fecha = date('2030-07-05'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-16'})
MERGE (visitante:Equipo {codigo: 'EQ-32'})
MERGE (s:Sede {codigo: 'SED-16'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0181'})
SET ev.tipo = 'Gol',
    ev.minuto = 17
MERGE (p:Partido {codigo: 'PAR-0091'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0182'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 36
MERGE (p:Partido {codigo: 'PAR-0091'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0092'})
SET p.fecha = date('2030-07-05'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-16'})
MERGE (visitante:Equipo {codigo: 'EQ-48'})
MERGE (s:Sede {codigo: 'SED-16'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0183'})
SET ev.tipo = 'Gol',
    ev.minuto = 24
MERGE (p:Partido {codigo: 'PAR-0092'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0184'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 47
MERGE (p:Partido {codigo: 'PAR-0092'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0093'})
SET p.fecha = date('2030-07-06'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-16'})
MERGE (visitante:Equipo {codigo: 'EQ-64'})
MERGE (s:Sede {codigo: 'SED-16'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0185'})
SET ev.tipo = 'Gol',
    ev.minuto = 31
MERGE (p:Partido {codigo: 'PAR-0093'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0186'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 58
MERGE (p:Partido {codigo: 'PAR-0093'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0094'})
SET p.fecha = date('2030-07-06'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-32'})
MERGE (visitante:Equipo {codigo: 'EQ-48'})
MERGE (s:Sede {codigo: 'SED-16'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0187'})
SET ev.tipo = 'Gol',
    ev.minuto = 38
MERGE (p:Partido {codigo: 'PAR-0094'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0188'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 69
MERGE (p:Partido {codigo: 'PAR-0094'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0095'})
SET p.fecha = date('2030-07-06'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-32'})
MERGE (visitante:Equipo {codigo: 'EQ-64'})
MERGE (s:Sede {codigo: 'SED-16'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0189'})
SET ev.tipo = 'Gol',
    ev.minuto = 45
MERGE (p:Partido {codigo: 'PAR-0095'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0190'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 80
MERGE (p:Partido {codigo: 'PAR-0095'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (p:Partido {codigo: 'PAR-0096'})
SET p.fecha = date('2030-07-06'),
    p.fase = 'Grupos'
MERGE (local:Equipo {codigo: 'EQ-48'})
MERGE (visitante:Equipo {codigo: 'EQ-64'})
MERGE (s:Sede {codigo: 'SED-16'})
MERGE (p)-[:DISPUTA]->(local)
MERGE (p)-[:DISPUTA]->(visitante)
MERGE (p)-[:SE_JUEGA_EN]->(s);

MERGE (ev:Evento {codigo: 'EVE-0191'})
SET ev.tipo = 'Gol',
    ev.minuto = 52
MERGE (p:Partido {codigo: 'PAR-0096'})
MERGE (ev)-[:OCURRE_EN]->(p);

MERGE (ev:Evento {codigo: 'EVE-0192'})
SET ev.tipo = 'Tarjeta amarilla',
    ev.minuto = 21
MERGE (p:Partido {codigo: 'PAR-0096'})
MERGE (ev)-[:OCURRE_EN]->(p);

