// ======================================================
// Fixture 2030 - Hito 5
// Carga reproducible de Equipos, Jugadores y pertenencias
// Generada a partir de los mismos datos utilizados en el Hito 4
// ======================================================

// 1. CARGA DE 64 EQUIPOS

MERGE (e:Equipo {codigo: 'EQ-01'})
SET e.nombre = 'Argentina',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-02'})
SET e.nombre = 'Bolivia',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-03'})
SET e.nombre = 'Brasil',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-04'})
SET e.nombre = 'Chile',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-05'})
SET e.nombre = 'Colombia',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-06'})
SET e.nombre = 'Ecuador',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-07'})
SET e.nombre = 'Paraguay',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-08'})
SET e.nombre = 'Perú',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-09'})
SET e.nombre = 'Uruguay',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-10'})
SET e.nombre = 'Venezuela',
    e.confederacion = 'CONMEBOL';

MERGE (e:Equipo {codigo: 'EQ-11'})
SET e.nombre = 'Alemania',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-12'})
SET e.nombre = 'España',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-13'})
SET e.nombre = 'Francia',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-14'})
SET e.nombre = 'Inglaterra',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-15'})
SET e.nombre = 'Italia',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-16'})
SET e.nombre = 'Portugal',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-17'})
SET e.nombre = 'Países Bajos',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-18'})
SET e.nombre = 'Bélgica',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-19'})
SET e.nombre = 'Croacia',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-20'})
SET e.nombre = 'Suiza',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-21'})
SET e.nombre = 'Dinamarca',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-22'})
SET e.nombre = 'Serbia',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-23'})
SET e.nombre = 'Austria',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-24'})
SET e.nombre = 'Polonia',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-25'})
SET e.nombre = 'Ucrania',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-26'})
SET e.nombre = 'Noruega',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-27'})
SET e.nombre = 'Suecia',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-28'})
SET e.nombre = 'Turquía',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-29'})
SET e.nombre = 'Escocia',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-30'})
SET e.nombre = 'República Checa',
    e.confederacion = 'UEFA';

MERGE (e:Equipo {codigo: 'EQ-31'})
SET e.nombre = 'Canadá',
    e.confederacion = 'CONCACAF';

MERGE (e:Equipo {codigo: 'EQ-32'})
SET e.nombre = 'Estados Unidos',
    e.confederacion = 'CONCACAF';

MERGE (e:Equipo {codigo: 'EQ-33'})
SET e.nombre = 'México',
    e.confederacion = 'CONCACAF';

MERGE (e:Equipo {codigo: 'EQ-34'})
SET e.nombre = 'Costa Rica',
    e.confederacion = 'CONCACAF';

MERGE (e:Equipo {codigo: 'EQ-35'})
SET e.nombre = 'Panamá',
    e.confederacion = 'CONCACAF';

MERGE (e:Equipo {codigo: 'EQ-36'})
SET e.nombre = 'Honduras',
    e.confederacion = 'CONCACAF';

MERGE (e:Equipo {codigo: 'EQ-37'})
SET e.nombre = 'Jamaica',
    e.confederacion = 'CONCACAF';

MERGE (e:Equipo {codigo: 'EQ-38'})
SET e.nombre = 'Trinidad y Tobago',
    e.confederacion = 'CONCACAF';

MERGE (e:Equipo {codigo: 'EQ-39'})
SET e.nombre = 'Marruecos',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-40'})
SET e.nombre = 'Argelia',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-41'})
SET e.nombre = 'Túnez',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-42'})
SET e.nombre = 'Egipto',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-43'})
SET e.nombre = 'Senegal',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-44'})
SET e.nombre = 'Nigeria',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-45'})
SET e.nombre = 'Ghana',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-46'})
SET e.nombre = 'Camerún',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-47'})
SET e.nombre = 'Costa de Marfil',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-48'})
SET e.nombre = 'Sudáfrica',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-49'})
SET e.nombre = 'Mali',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-50'})
SET e.nombre = 'República Democrática del Congo',
    e.confederacion = 'CAF';

MERGE (e:Equipo {codigo: 'EQ-51'})
SET e.nombre = 'Japón',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-52'})
SET e.nombre = 'Corea del Sur',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-53'})
SET e.nombre = 'China',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-54'})
SET e.nombre = 'Australia',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-55'})
SET e.nombre = 'Irán',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-56'})
SET e.nombre = 'Arabia Saudita',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-57'})
SET e.nombre = 'Catar',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-58'})
SET e.nombre = 'Irak',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-59'})
SET e.nombre = 'Uzbekistán',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-60'})
SET e.nombre = 'Emiratos Árabes Unidos',
    e.confederacion = 'AFC';

MERGE (e:Equipo {codigo: 'EQ-61'})
SET e.nombre = 'Nueva Zelanda',
    e.confederacion = 'OFC';

MERGE (e:Equipo {codigo: 'EQ-62'})
SET e.nombre = 'Nueva Caledonia',
    e.confederacion = 'OFC';

MERGE (e:Equipo {codigo: 'EQ-63'})
SET e.nombre = 'Fiyi',
    e.confederacion = 'OFC';

MERGE (e:Equipo {codigo: 'EQ-64'})
SET e.nombre = 'Islas Salomón',
    e.confederacion = 'OFC';

// 2. CARGA DE 1.024 JUGADORES Y SUS RELACIONES

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0001'})
SET j.nombre = 'Alejandro García',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0002'})
SET j.nombre = 'Bruno Fernández',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0003'})
SET j.nombre = 'Carlos González',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0004'})
SET j.nombre = 'Diego Rodríguez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0005'})
SET j.nombre = 'Emiliano López',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0006'})
SET j.nombre = 'Facundo Martínez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0007'})
SET j.nombre = 'Gabriel Sánchez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0008'})
SET j.nombre = 'Joaquín Pérez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0009'})
SET j.nombre = 'Lautaro Romero',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0010'})
SET j.nombre = 'Mateo Díaz',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0011'})
SET j.nombre = 'Nicolás Torres',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0012'})
SET j.nombre = 'Ramiro Álvarez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0013'})
SET j.nombre = 'Santiago Ruiz',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0014'})
SET j.nombre = 'Tomás Herrera',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0015'})
SET j.nombre = 'Valentín Castro',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-01'})
MERGE (j:Jugador {codigo: 'JUG-0016'})
SET j.nombre = 'Martín Silva',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0017'})
SET j.nombre = 'Alejandro Fernández',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0018'})
SET j.nombre = 'Bruno González',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0019'})
SET j.nombre = 'Carlos Rodríguez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0020'})
SET j.nombre = 'Diego López',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0021'})
SET j.nombre = 'Emiliano Martínez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0022'})
SET j.nombre = 'Facundo Sánchez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0023'})
SET j.nombre = 'Gabriel Pérez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0024'})
SET j.nombre = 'Joaquín Romero',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0025'})
SET j.nombre = 'Lautaro Díaz',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0026'})
SET j.nombre = 'Mateo Torres',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0027'})
SET j.nombre = 'Nicolás Álvarez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0028'})
SET j.nombre = 'Ramiro Ruiz',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0029'})
SET j.nombre = 'Santiago Herrera',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0030'})
SET j.nombre = 'Tomás Castro',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0031'})
SET j.nombre = 'Valentín Silva',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-02'})
MERGE (j:Jugador {codigo: 'JUG-0032'})
SET j.nombre = 'Martín García',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0033'})
SET j.nombre = 'André Almeida',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0034'})
SET j.nombre = 'Bruno Barbosa',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0035'})
SET j.nombre = 'Caio Carvalho',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0036'})
SET j.nombre = 'Diogo Costa',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0037'})
SET j.nombre = 'Eduardo Fernandes',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0038'})
SET j.nombre = 'Fábio Ferreira',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0039'})
SET j.nombre = 'Gabriel Gomes',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0040'})
SET j.nombre = 'Henrique Lima',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0041'})
SET j.nombre = 'João Martins',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0042'})
SET j.nombre = 'Leonardo Mendes',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0043'})
SET j.nombre = 'Lucas Moreira',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0044'})
SET j.nombre = 'Mateus Oliveira',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0045'})
SET j.nombre = 'Miguel Pereira',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0046'})
SET j.nombre = 'Rafael Ribeiro',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0047'})
SET j.nombre = 'Tiago Rocha',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-03'})
MERGE (j:Jugador {codigo: 'JUG-0048'})
SET j.nombre = 'Vinícius Santos',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0049'})
SET j.nombre = 'Alejandro González',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0050'})
SET j.nombre = 'Bruno Rodríguez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0051'})
SET j.nombre = 'Carlos López',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0052'})
SET j.nombre = 'Diego Martínez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0053'})
SET j.nombre = 'Emiliano Sánchez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0054'})
SET j.nombre = 'Facundo Pérez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0055'})
SET j.nombre = 'Gabriel Romero',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0056'})
SET j.nombre = 'Joaquín Díaz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0057'})
SET j.nombre = 'Lautaro Torres',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0058'})
SET j.nombre = 'Mateo Álvarez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0059'})
SET j.nombre = 'Nicolás Ruiz',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0060'})
SET j.nombre = 'Ramiro Herrera',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0061'})
SET j.nombre = 'Santiago Castro',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0062'})
SET j.nombre = 'Tomás Silva',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0063'})
SET j.nombre = 'Valentín García',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-04'})
MERGE (j:Jugador {codigo: 'JUG-0064'})
SET j.nombre = 'Martín Fernández',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0065'})
SET j.nombre = 'Alejandro Rodríguez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0066'})
SET j.nombre = 'Bruno López',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0067'})
SET j.nombre = 'Carlos Martínez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0068'})
SET j.nombre = 'Diego Sánchez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0069'})
SET j.nombre = 'Emiliano Pérez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0070'})
SET j.nombre = 'Facundo Romero',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0071'})
SET j.nombre = 'Gabriel Díaz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0072'})
SET j.nombre = 'Joaquín Torres',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0073'})
SET j.nombre = 'Lautaro Álvarez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0074'})
SET j.nombre = 'Mateo Ruiz',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0075'})
SET j.nombre = 'Nicolás Herrera',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0076'})
SET j.nombre = 'Ramiro Castro',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0077'})
SET j.nombre = 'Santiago Silva',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0078'})
SET j.nombre = 'Tomás García',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0079'})
SET j.nombre = 'Valentín Fernández',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-05'})
MERGE (j:Jugador {codigo: 'JUG-0080'})
SET j.nombre = 'Martín González',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0081'})
SET j.nombre = 'Alejandro López',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0082'})
SET j.nombre = 'Bruno Martínez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0083'})
SET j.nombre = 'Carlos Sánchez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0084'})
SET j.nombre = 'Diego Pérez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0085'})
SET j.nombre = 'Emiliano Romero',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0086'})
SET j.nombre = 'Facundo Díaz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0087'})
SET j.nombre = 'Gabriel Torres',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0088'})
SET j.nombre = 'Joaquín Álvarez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0089'})
SET j.nombre = 'Lautaro Ruiz',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0090'})
SET j.nombre = 'Mateo Herrera',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0091'})
SET j.nombre = 'Nicolás Castro',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0092'})
SET j.nombre = 'Ramiro Silva',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0093'})
SET j.nombre = 'Santiago García',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0094'})
SET j.nombre = 'Tomás Fernández',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0095'})
SET j.nombre = 'Valentín González',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-06'})
MERGE (j:Jugador {codigo: 'JUG-0096'})
SET j.nombre = 'Martín Rodríguez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0097'})
SET j.nombre = 'Alejandro Martínez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0098'})
SET j.nombre = 'Bruno Sánchez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0099'})
SET j.nombre = 'Carlos Pérez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0100'})
SET j.nombre = 'Diego Romero',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0101'})
SET j.nombre = 'Emiliano Díaz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0102'})
SET j.nombre = 'Facundo Torres',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0103'})
SET j.nombre = 'Gabriel Álvarez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0104'})
SET j.nombre = 'Joaquín Ruiz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0105'})
SET j.nombre = 'Lautaro Herrera',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0106'})
SET j.nombre = 'Mateo Castro',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0107'})
SET j.nombre = 'Nicolás Silva',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0108'})
SET j.nombre = 'Ramiro García',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0109'})
SET j.nombre = 'Santiago Fernández',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0110'})
SET j.nombre = 'Tomás González',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0111'})
SET j.nombre = 'Valentín Rodríguez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-07'})
MERGE (j:Jugador {codigo: 'JUG-0112'})
SET j.nombre = 'Martín López',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0113'})
SET j.nombre = 'Alejandro Sánchez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0114'})
SET j.nombre = 'Bruno Pérez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0115'})
SET j.nombre = 'Carlos Romero',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0116'})
SET j.nombre = 'Diego Díaz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0117'})
SET j.nombre = 'Emiliano Torres',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0118'})
SET j.nombre = 'Facundo Álvarez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0119'})
SET j.nombre = 'Gabriel Ruiz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0120'})
SET j.nombre = 'Joaquín Herrera',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0121'})
SET j.nombre = 'Lautaro Castro',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0122'})
SET j.nombre = 'Mateo Silva',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0123'})
SET j.nombre = 'Nicolás García',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0124'})
SET j.nombre = 'Ramiro Fernández',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0125'})
SET j.nombre = 'Santiago González',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0126'})
SET j.nombre = 'Tomás Rodríguez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0127'})
SET j.nombre = 'Valentín López',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-08'})
MERGE (j:Jugador {codigo: 'JUG-0128'})
SET j.nombre = 'Martín Martínez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0129'})
SET j.nombre = 'Alejandro Pérez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0130'})
SET j.nombre = 'Bruno Romero',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0131'})
SET j.nombre = 'Carlos Díaz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0132'})
SET j.nombre = 'Diego Torres',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0133'})
SET j.nombre = 'Emiliano Álvarez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0134'})
SET j.nombre = 'Facundo Ruiz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0135'})
SET j.nombre = 'Gabriel Herrera',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0136'})
SET j.nombre = 'Joaquín Castro',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0137'})
SET j.nombre = 'Lautaro Silva',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0138'})
SET j.nombre = 'Mateo García',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0139'})
SET j.nombre = 'Nicolás Fernández',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0140'})
SET j.nombre = 'Ramiro González',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0141'})
SET j.nombre = 'Santiago Rodríguez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0142'})
SET j.nombre = 'Tomás López',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0143'})
SET j.nombre = 'Valentín Martínez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-09'})
MERGE (j:Jugador {codigo: 'JUG-0144'})
SET j.nombre = 'Martín Sánchez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0145'})
SET j.nombre = 'Alejandro Romero',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0146'})
SET j.nombre = 'Bruno Díaz',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0147'})
SET j.nombre = 'Carlos Torres',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0148'})
SET j.nombre = 'Diego Álvarez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0149'})
SET j.nombre = 'Emiliano Ruiz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0150'})
SET j.nombre = 'Facundo Herrera',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0151'})
SET j.nombre = 'Gabriel Castro',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0152'})
SET j.nombre = 'Joaquín Silva',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0153'})
SET j.nombre = 'Lautaro García',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0154'})
SET j.nombre = 'Mateo Fernández',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0155'})
SET j.nombre = 'Nicolás González',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0156'})
SET j.nombre = 'Ramiro Rodríguez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0157'})
SET j.nombre = 'Santiago López',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0158'})
SET j.nombre = 'Tomás Martínez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0159'})
SET j.nombre = 'Valentín Sánchez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-10'})
MERGE (j:Jugador {codigo: 'JUG-0160'})
SET j.nombre = 'Martín Pérez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0161'})
SET j.nombre = 'Alexander Bauer',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0162'})
SET j.nombre = 'Benjamin Becker',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0163'})
SET j.nombre = 'Elias Braun',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0164'})
SET j.nombre = 'Felix Fischer',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0165'})
SET j.nombre = 'Florian Hartmann',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0166'})
SET j.nombre = 'Jonas Hoffmann',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0167'})
SET j.nombre = 'Julian Keller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0168'})
SET j.nombre = 'Leon Klein',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0169'})
SET j.nombre = 'Lukas Koch',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0170'})
SET j.nombre = 'Maximilian Krüger',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0171'})
SET j.nombre = 'Nico Lehmann',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0172'})
SET j.nombre = 'Noah Meyer',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0173'})
SET j.nombre = 'Sebastian Richter',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0174'})
SET j.nombre = 'Simon Schneider',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0175'})
SET j.nombre = 'Tobias Wagner',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-11'})
MERGE (j:Jugador {codigo: 'JUG-0176'})
SET j.nombre = 'Yannick Weber',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0177'})
SET j.nombre = 'Alejandro Díaz',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0178'})
SET j.nombre = 'Bruno Torres',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0179'})
SET j.nombre = 'Carlos Álvarez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0180'})
SET j.nombre = 'Diego Ruiz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0181'})
SET j.nombre = 'Emiliano Herrera',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0182'})
SET j.nombre = 'Facundo Castro',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0183'})
SET j.nombre = 'Gabriel Silva',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0184'})
SET j.nombre = 'Joaquín García',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0185'})
SET j.nombre = 'Lautaro Fernández',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0186'})
SET j.nombre = 'Mateo González',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0187'})
SET j.nombre = 'Nicolás Rodríguez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0188'})
SET j.nombre = 'Ramiro López',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0189'})
SET j.nombre = 'Santiago Martínez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0190'})
SET j.nombre = 'Tomás Sánchez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0191'})
SET j.nombre = 'Valentín Pérez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-12'})
MERGE (j:Jugador {codigo: 'JUG-0192'})
SET j.nombre = 'Martín Romero',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0193'})
SET j.nombre = 'Adrien Bernard',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0194'})
SET j.nombre = 'Antoine Bertrand',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0195'})
SET j.nombre = 'Baptiste Blanc',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0196'})
SET j.nombre = 'Clément Dubois',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0197'})
SET j.nombre = 'Enzo Dupont',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0198'})
SET j.nombre = 'Étienne Fontaine',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0199'})
SET j.nombre = 'Hugo Fournier',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0200'})
SET j.nombre = 'Jules Laurent',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0201'})
SET j.nombre = 'Laurent Lefèvre',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0202'})
SET j.nombre = 'Léo Leroy',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0203'})
SET j.nombre = 'Lucas Martin',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0204'})
SET j.nombre = 'Mathis Mercier',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0205'})
SET j.nombre = 'Nathan Moreau',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0206'})
SET j.nombre = 'Rémi Petit',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0207'})
SET j.nombre = 'Théo Robert',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-13'})
MERGE (j:Jugador {codigo: 'JUG-0208'})
SET j.nombre = 'Victor Simon',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0209'})
SET j.nombre = 'Adam Anderson',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0210'})
SET j.nombre = 'Benjamin Brown',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0211'})
SET j.nombre = 'Callum Campbell',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0212'})
SET j.nombre = 'Daniel Clark',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0213'})
SET j.nombre = 'Ethan Davies',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0214'})
SET j.nombre = 'George Evans',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0215'})
SET j.nombre = 'Harry Harris',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0216'})
SET j.nombre = 'Jack Jackson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0217'})
SET j.nombre = 'James Johnson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0218'})
SET j.nombre = 'Liam Miller',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0219'})
SET j.nombre = 'Mason Mitchell',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0220'})
SET j.nombre = 'Noah Robinson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0221'})
SET j.nombre = 'Oliver Smith',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0222'})
SET j.nombre = 'Samuel Taylor',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0223'})
SET j.nombre = 'Thomas Thompson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-14'})
MERGE (j:Jugador {codigo: 'JUG-0224'})
SET j.nombre = 'William Wilson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0225'})
SET j.nombre = 'Alessandro Bianchi',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0226'})
SET j.nombre = 'Andrea Colombo',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0227'})
SET j.nombre = 'Davide Conti',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0228'})
SET j.nombre = 'Federico De Luca',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0229'})
SET j.nombre = 'Francesco Esposito',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0230'})
SET j.nombre = 'Gabriele Ferrari',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0231'})
SET j.nombre = 'Giacomo Gallo',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0232'})
SET j.nombre = 'Giovanni Greco',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0233'})
SET j.nombre = 'Leonardo Lombardi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0234'})
SET j.nombre = 'Lorenzo Mancini',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0235'})
SET j.nombre = 'Luca Marino',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0236'})
SET j.nombre = 'Marco Moretti',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0237'})
SET j.nombre = 'Matteo Ricci',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0238'})
SET j.nombre = 'Riccardo Romano',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0239'})
SET j.nombre = 'Simone Rossi',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-15'})
MERGE (j:Jugador {codigo: 'JUG-0240'})
SET j.nombre = 'Tommaso Villa',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0241'})
SET j.nombre = 'André Barbosa',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0242'})
SET j.nombre = 'Bruno Carvalho',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0243'})
SET j.nombre = 'Caio Costa',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0244'})
SET j.nombre = 'Diogo Fernandes',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0245'})
SET j.nombre = 'Eduardo Ferreira',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0246'})
SET j.nombre = 'Fábio Gomes',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0247'})
SET j.nombre = 'Gabriel Lima',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0248'})
SET j.nombre = 'Henrique Martins',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0249'})
SET j.nombre = 'João Mendes',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0250'})
SET j.nombre = 'Leonardo Moreira',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0251'})
SET j.nombre = 'Lucas Oliveira',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0252'})
SET j.nombre = 'Mateus Pereira',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0253'})
SET j.nombre = 'Miguel Ribeiro',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0254'})
SET j.nombre = 'Rafael Rocha',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0255'})
SET j.nombre = 'Tiago Santos',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-16'})
MERGE (j:Jugador {codigo: 'JUG-0256'})
SET j.nombre = 'Vinícius Almeida',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0257'})
SET j.nombre = 'Alexander Becker',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0258'})
SET j.nombre = 'Benjamin Braun',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0259'})
SET j.nombre = 'Elias Fischer',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0260'})
SET j.nombre = 'Felix Hartmann',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0261'})
SET j.nombre = 'Florian Hoffmann',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0262'})
SET j.nombre = 'Jonas Keller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0263'})
SET j.nombre = 'Julian Klein',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0264'})
SET j.nombre = 'Leon Koch',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0265'})
SET j.nombre = 'Lukas Krüger',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0266'})
SET j.nombre = 'Maximilian Lehmann',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0267'})
SET j.nombre = 'Nico Meyer',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0268'})
SET j.nombre = 'Noah Richter',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0269'})
SET j.nombre = 'Sebastian Schneider',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0270'})
SET j.nombre = 'Simon Wagner',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0271'})
SET j.nombre = 'Tobias Weber',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-17'})
MERGE (j:Jugador {codigo: 'JUG-0272'})
SET j.nombre = 'Yannick Bauer',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0273'})
SET j.nombre = 'Adrien Bertrand',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0274'})
SET j.nombre = 'Antoine Blanc',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0275'})
SET j.nombre = 'Baptiste Dubois',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0276'})
SET j.nombre = 'Clément Dupont',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0277'})
SET j.nombre = 'Enzo Fontaine',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0278'})
SET j.nombre = 'Étienne Fournier',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0279'})
SET j.nombre = 'Hugo Laurent',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0280'})
SET j.nombre = 'Jules Lefèvre',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0281'})
SET j.nombre = 'Laurent Leroy',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0282'})
SET j.nombre = 'Léo Martin',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0283'})
SET j.nombre = 'Lucas Mercier',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0284'})
SET j.nombre = 'Mathis Moreau',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0285'})
SET j.nombre = 'Nathan Petit',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0286'})
SET j.nombre = 'Rémi Robert',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0287'})
SET j.nombre = 'Théo Simon',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-18'})
MERGE (j:Jugador {codigo: 'JUG-0288'})
SET j.nombre = 'Victor Bernard',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0289'})
SET j.nombre = 'Aleksandar Horvat',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0290'})
SET j.nombre = 'Andrija Jovanović',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0291'})
SET j.nombre = 'Bohdan Kovač',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0292'})
SET j.nombre = 'Dario Kowalski',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0293'})
SET j.nombre = 'Ivan Marković',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0294'})
SET j.nombre = 'Jakub Miletić',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0295'})
SET j.nombre = 'Luka Novak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0296'})
SET j.nombre = 'Marko Nowak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0297'})
SET j.nombre = 'Matej Petrović',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0298'})
SET j.nombre = 'Milan Popović',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0299'})
SET j.nombre = 'Nikola Shevchenko',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0300'})
SET j.nombre = 'Oleksandr Sokolov',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0301'})
SET j.nombre = 'Pavel Stanić',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0302'})
SET j.nombre = 'Petar Vuković',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0303'})
SET j.nombre = 'Tomas Zieliński',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-19'})
MERGE (j:Jugador {codigo: 'JUG-0304'})
SET j.nombre = 'Viktor Živković',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0305'})
SET j.nombre = 'Alexander Braun',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0306'})
SET j.nombre = 'Benjamin Fischer',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0307'})
SET j.nombre = 'Elias Hartmann',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0308'})
SET j.nombre = 'Felix Hoffmann',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0309'})
SET j.nombre = 'Florian Keller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0310'})
SET j.nombre = 'Jonas Klein',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0311'})
SET j.nombre = 'Julian Koch',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0312'})
SET j.nombre = 'Leon Krüger',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0313'})
SET j.nombre = 'Lukas Lehmann',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0314'})
SET j.nombre = 'Maximilian Meyer',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0315'})
SET j.nombre = 'Nico Richter',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0316'})
SET j.nombre = 'Noah Schneider',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0317'})
SET j.nombre = 'Sebastian Wagner',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0318'})
SET j.nombre = 'Simon Weber',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0319'})
SET j.nombre = 'Tobias Bauer',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-20'})
MERGE (j:Jugador {codigo: 'JUG-0320'})
SET j.nombre = 'Yannick Becker',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0321'})
SET j.nombre = 'Anders Andersen',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0322'})
SET j.nombre = 'Axel Berg',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0323'})
SET j.nombre = 'Bjørn Dahl',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0324'})
SET j.nombre = 'Elias Eriksen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0325'})
SET j.nombre = 'Emil Hansen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0326'})
SET j.nombre = 'Erik Jensen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0327'})
SET j.nombre = 'Gustav Kristensen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0328'})
SET j.nombre = 'Henrik Larsen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0329'})
SET j.nombre = 'Isak Lindberg',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0330'})
SET j.nombre = 'Johan Lund',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0331'})
SET j.nombre = 'Kasper Nielsen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0332'})
SET j.nombre = 'Magnus Olsen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0333'})
SET j.nombre = 'Mikkel Pedersen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0334'})
SET j.nombre = 'Oskar Svensson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0335'})
SET j.nombre = 'Søren Sørensen',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-21'})
MERGE (j:Jugador {codigo: 'JUG-0336'})
SET j.nombre = 'Viktor Vik',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0337'})
SET j.nombre = 'Aleksandar Jovanović',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0338'})
SET j.nombre = 'Andrija Kovač',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0339'})
SET j.nombre = 'Bohdan Kowalski',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0340'})
SET j.nombre = 'Dario Marković',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0341'})
SET j.nombre = 'Ivan Miletić',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0342'})
SET j.nombre = 'Jakub Novak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0343'})
SET j.nombre = 'Luka Nowak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0344'})
SET j.nombre = 'Marko Petrović',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0345'})
SET j.nombre = 'Matej Popović',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0346'})
SET j.nombre = 'Milan Shevchenko',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0347'})
SET j.nombre = 'Nikola Sokolov',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0348'})
SET j.nombre = 'Oleksandr Stanić',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0349'})
SET j.nombre = 'Pavel Vuković',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0350'})
SET j.nombre = 'Petar Zieliński',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0351'})
SET j.nombre = 'Tomas Živković',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-22'})
MERGE (j:Jugador {codigo: 'JUG-0352'})
SET j.nombre = 'Viktor Horvat',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0353'})
SET j.nombre = 'Alexander Fischer',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0354'})
SET j.nombre = 'Benjamin Hartmann',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0355'})
SET j.nombre = 'Elias Hoffmann',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0356'})
SET j.nombre = 'Felix Keller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0357'})
SET j.nombre = 'Florian Klein',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0358'})
SET j.nombre = 'Jonas Koch',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0359'})
SET j.nombre = 'Julian Krüger',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0360'})
SET j.nombre = 'Leon Lehmann',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0361'})
SET j.nombre = 'Lukas Meyer',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0362'})
SET j.nombre = 'Maximilian Richter',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0363'})
SET j.nombre = 'Nico Schneider',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0364'})
SET j.nombre = 'Noah Wagner',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0365'})
SET j.nombre = 'Sebastian Weber',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0366'})
SET j.nombre = 'Simon Bauer',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0367'})
SET j.nombre = 'Tobias Becker',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-23'})
MERGE (j:Jugador {codigo: 'JUG-0368'})
SET j.nombre = 'Yannick Braun',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0369'})
SET j.nombre = 'Aleksandar Kovač',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0370'})
SET j.nombre = 'Andrija Kowalski',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0371'})
SET j.nombre = 'Bohdan Marković',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0372'})
SET j.nombre = 'Dario Miletić',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0373'})
SET j.nombre = 'Ivan Novak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0374'})
SET j.nombre = 'Jakub Nowak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0375'})
SET j.nombre = 'Luka Petrović',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0376'})
SET j.nombre = 'Marko Popović',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0377'})
SET j.nombre = 'Matej Shevchenko',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0378'})
SET j.nombre = 'Milan Sokolov',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0379'})
SET j.nombre = 'Nikola Stanić',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0380'})
SET j.nombre = 'Oleksandr Vuković',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0381'})
SET j.nombre = 'Pavel Zieliński',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0382'})
SET j.nombre = 'Petar Živković',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0383'})
SET j.nombre = 'Tomas Horvat',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-24'})
MERGE (j:Jugador {codigo: 'JUG-0384'})
SET j.nombre = 'Viktor Jovanović',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0385'})
SET j.nombre = 'Aleksandar Kowalski',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0386'})
SET j.nombre = 'Andrija Marković',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0387'})
SET j.nombre = 'Bohdan Miletić',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0388'})
SET j.nombre = 'Dario Novak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0389'})
SET j.nombre = 'Ivan Nowak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0390'})
SET j.nombre = 'Jakub Petrović',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0391'})
SET j.nombre = 'Luka Popović',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0392'})
SET j.nombre = 'Marko Shevchenko',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0393'})
SET j.nombre = 'Matej Sokolov',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0394'})
SET j.nombre = 'Milan Stanić',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0395'})
SET j.nombre = 'Nikola Vuković',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0396'})
SET j.nombre = 'Oleksandr Zieliński',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0397'})
SET j.nombre = 'Pavel Živković',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0398'})
SET j.nombre = 'Petar Horvat',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0399'})
SET j.nombre = 'Tomas Jovanović',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-25'})
MERGE (j:Jugador {codigo: 'JUG-0400'})
SET j.nombre = 'Viktor Kovač',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0401'})
SET j.nombre = 'Anders Berg',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0402'})
SET j.nombre = 'Axel Dahl',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0403'})
SET j.nombre = 'Bjørn Eriksen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0404'})
SET j.nombre = 'Elias Hansen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0405'})
SET j.nombre = 'Emil Jensen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0406'})
SET j.nombre = 'Erik Kristensen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0407'})
SET j.nombre = 'Gustav Larsen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0408'})
SET j.nombre = 'Henrik Lindberg',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0409'})
SET j.nombre = 'Isak Lund',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0410'})
SET j.nombre = 'Johan Nielsen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0411'})
SET j.nombre = 'Kasper Olsen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0412'})
SET j.nombre = 'Magnus Pedersen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0413'})
SET j.nombre = 'Mikkel Svensson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0414'})
SET j.nombre = 'Oskar Sørensen',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0415'})
SET j.nombre = 'Søren Vik',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-26'})
MERGE (j:Jugador {codigo: 'JUG-0416'})
SET j.nombre = 'Viktor Andersen',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0417'})
SET j.nombre = 'Anders Dahl',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0418'})
SET j.nombre = 'Axel Eriksen',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0419'})
SET j.nombre = 'Bjørn Hansen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0420'})
SET j.nombre = 'Elias Jensen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0421'})
SET j.nombre = 'Emil Kristensen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0422'})
SET j.nombre = 'Erik Larsen',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0423'})
SET j.nombre = 'Gustav Lindberg',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0424'})
SET j.nombre = 'Henrik Lund',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0425'})
SET j.nombre = 'Isak Nielsen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0426'})
SET j.nombre = 'Johan Olsen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0427'})
SET j.nombre = 'Kasper Pedersen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0428'})
SET j.nombre = 'Magnus Svensson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0429'})
SET j.nombre = 'Mikkel Sørensen',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0430'})
SET j.nombre = 'Oskar Vik',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0431'})
SET j.nombre = 'Søren Andersen',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-27'})
MERGE (j:Jugador {codigo: 'JUG-0432'})
SET j.nombre = 'Viktor Berg',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0433'})
SET j.nombre = 'Ahmet Aydın',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0434'})
SET j.nombre = 'Ali Çelik',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0435'})
SET j.nombre = 'Arda Demir',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0436'})
SET j.nombre = 'Ayberk Erdoğan',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0437'})
SET j.nombre = 'Burak Güneş',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0438'})
SET j.nombre = 'Can Kaya',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0439'})
SET j.nombre = 'Emre Kılıç',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0440'})
SET j.nombre = 'Eren Koç',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0441'})
SET j.nombre = 'Hakan Özcan',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0442'})
SET j.nombre = 'Kerem Polat',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0443'})
SET j.nombre = 'Mehmet Şahin',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0444'})
SET j.nombre = 'Mert Tekin',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0445'})
SET j.nombre = 'Oğuz Toprak',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0446'})
SET j.nombre = 'Onur Yıldırım',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0447'})
SET j.nombre = 'Selim Yılmaz',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-28'})
MERGE (j:Jugador {codigo: 'JUG-0448'})
SET j.nombre = 'Yusuf Zengin',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0449'})
SET j.nombre = 'Adam Brown',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0450'})
SET j.nombre = 'Benjamin Campbell',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0451'})
SET j.nombre = 'Callum Clark',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0452'})
SET j.nombre = 'Daniel Davies',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0453'})
SET j.nombre = 'Ethan Evans',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0454'})
SET j.nombre = 'George Harris',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0455'})
SET j.nombre = 'Harry Jackson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0456'})
SET j.nombre = 'Jack Johnson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0457'})
SET j.nombre = 'James Miller',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0458'})
SET j.nombre = 'Liam Mitchell',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0459'})
SET j.nombre = 'Mason Robinson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0460'})
SET j.nombre = 'Noah Smith',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0461'})
SET j.nombre = 'Oliver Taylor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0462'})
SET j.nombre = 'Samuel Thompson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0463'})
SET j.nombre = 'Thomas Wilson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-29'})
MERGE (j:Jugador {codigo: 'JUG-0464'})
SET j.nombre = 'William Anderson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0465'})
SET j.nombre = 'Aleksandar Marković',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0466'})
SET j.nombre = 'Andrija Miletić',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0467'})
SET j.nombre = 'Bohdan Novak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0468'})
SET j.nombre = 'Dario Nowak',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0469'})
SET j.nombre = 'Ivan Petrović',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0470'})
SET j.nombre = 'Jakub Popović',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0471'})
SET j.nombre = 'Luka Shevchenko',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0472'})
SET j.nombre = 'Marko Sokolov',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0473'})
SET j.nombre = 'Matej Stanić',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0474'})
SET j.nombre = 'Milan Vuković',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0475'})
SET j.nombre = 'Nikola Zieliński',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0476'})
SET j.nombre = 'Oleksandr Živković',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0477'})
SET j.nombre = 'Pavel Horvat',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0478'})
SET j.nombre = 'Petar Jovanović',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0479'})
SET j.nombre = 'Tomas Kovač',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-30'})
MERGE (j:Jugador {codigo: 'JUG-0480'})
SET j.nombre = 'Viktor Kowalski',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0481'})
SET j.nombre = 'Adam Campbell',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0482'})
SET j.nombre = 'Benjamin Clark',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0483'})
SET j.nombre = 'Callum Davies',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0484'})
SET j.nombre = 'Daniel Evans',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0485'})
SET j.nombre = 'Ethan Harris',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0486'})
SET j.nombre = 'George Jackson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0487'})
SET j.nombre = 'Harry Johnson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0488'})
SET j.nombre = 'Jack Miller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0489'})
SET j.nombre = 'James Mitchell',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0490'})
SET j.nombre = 'Liam Robinson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0491'})
SET j.nombre = 'Mason Smith',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0492'})
SET j.nombre = 'Noah Taylor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0493'})
SET j.nombre = 'Oliver Thompson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0494'})
SET j.nombre = 'Samuel Wilson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0495'})
SET j.nombre = 'Thomas Anderson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-31'})
MERGE (j:Jugador {codigo: 'JUG-0496'})
SET j.nombre = 'William Brown',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0497'})
SET j.nombre = 'Adam Clark',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0498'})
SET j.nombre = 'Benjamin Davies',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0499'})
SET j.nombre = 'Callum Evans',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0500'})
SET j.nombre = 'Daniel Harris',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0501'})
SET j.nombre = 'Ethan Jackson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0502'})
SET j.nombre = 'George Johnson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0503'})
SET j.nombre = 'Harry Miller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0504'})
SET j.nombre = 'Jack Mitchell',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0505'})
SET j.nombre = 'James Robinson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0506'})
SET j.nombre = 'Liam Smith',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0507'})
SET j.nombre = 'Mason Taylor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0508'})
SET j.nombre = 'Noah Thompson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0509'})
SET j.nombre = 'Oliver Wilson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0510'})
SET j.nombre = 'Samuel Anderson',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0511'})
SET j.nombre = 'Thomas Brown',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-32'})
MERGE (j:Jugador {codigo: 'JUG-0512'})
SET j.nombre = 'William Campbell',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0513'})
SET j.nombre = 'Alejandro Torres',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0514'})
SET j.nombre = 'Bruno Álvarez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0515'})
SET j.nombre = 'Carlos Ruiz',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0516'})
SET j.nombre = 'Diego Herrera',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0517'})
SET j.nombre = 'Emiliano Castro',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0518'})
SET j.nombre = 'Facundo Silva',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0519'})
SET j.nombre = 'Gabriel García',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0520'})
SET j.nombre = 'Joaquín Fernández',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0521'})
SET j.nombre = 'Lautaro González',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0522'})
SET j.nombre = 'Mateo Rodríguez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0523'})
SET j.nombre = 'Nicolás López',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0524'})
SET j.nombre = 'Ramiro Martínez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0525'})
SET j.nombre = 'Santiago Sánchez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0526'})
SET j.nombre = 'Tomás Pérez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0527'})
SET j.nombre = 'Valentín Romero',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-33'})
MERGE (j:Jugador {codigo: 'JUG-0528'})
SET j.nombre = 'Martín Díaz',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0529'})
SET j.nombre = 'Alejandro Álvarez',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0530'})
SET j.nombre = 'Bruno Ruiz',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0531'})
SET j.nombre = 'Carlos Herrera',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0532'})
SET j.nombre = 'Diego Castro',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0533'})
SET j.nombre = 'Emiliano Silva',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0534'})
SET j.nombre = 'Facundo García',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0535'})
SET j.nombre = 'Gabriel Fernández',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0536'})
SET j.nombre = 'Joaquín González',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0537'})
SET j.nombre = 'Lautaro Rodríguez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0538'})
SET j.nombre = 'Mateo López',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0539'})
SET j.nombre = 'Nicolás Martínez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0540'})
SET j.nombre = 'Ramiro Sánchez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0541'})
SET j.nombre = 'Santiago Pérez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0542'})
SET j.nombre = 'Tomás Romero',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0543'})
SET j.nombre = 'Valentín Díaz',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-34'})
MERGE (j:Jugador {codigo: 'JUG-0544'})
SET j.nombre = 'Martín Torres',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0545'})
SET j.nombre = 'Alejandro Ruiz',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0546'})
SET j.nombre = 'Bruno Herrera',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0547'})
SET j.nombre = 'Carlos Castro',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0548'})
SET j.nombre = 'Diego Silva',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0549'})
SET j.nombre = 'Emiliano García',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0550'})
SET j.nombre = 'Facundo Fernández',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0551'})
SET j.nombre = 'Gabriel González',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0552'})
SET j.nombre = 'Joaquín Rodríguez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0553'})
SET j.nombre = 'Lautaro López',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0554'})
SET j.nombre = 'Mateo Martínez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0555'})
SET j.nombre = 'Nicolás Sánchez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0556'})
SET j.nombre = 'Ramiro Pérez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0557'})
SET j.nombre = 'Santiago Romero',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0558'})
SET j.nombre = 'Tomás Díaz',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0559'})
SET j.nombre = 'Valentín Torres',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-35'})
MERGE (j:Jugador {codigo: 'JUG-0560'})
SET j.nombre = 'Martín Álvarez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0561'})
SET j.nombre = 'Alejandro Herrera',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0562'})
SET j.nombre = 'Bruno Castro',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0563'})
SET j.nombre = 'Carlos Silva',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0564'})
SET j.nombre = 'Diego García',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0565'})
SET j.nombre = 'Emiliano Fernández',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0566'})
SET j.nombre = 'Facundo González',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0567'})
SET j.nombre = 'Gabriel Rodríguez',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0568'})
SET j.nombre = 'Joaquín López',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0569'})
SET j.nombre = 'Lautaro Martínez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0570'})
SET j.nombre = 'Mateo Sánchez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0571'})
SET j.nombre = 'Nicolás Pérez',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0572'})
SET j.nombre = 'Ramiro Romero',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0573'})
SET j.nombre = 'Santiago Díaz',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0574'})
SET j.nombre = 'Tomás Torres',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0575'})
SET j.nombre = 'Valentín Álvarez',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-36'})
MERGE (j:Jugador {codigo: 'JUG-0576'})
SET j.nombre = 'Martín Ruiz',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0577'})
SET j.nombre = 'Adam Davies',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0578'})
SET j.nombre = 'Benjamin Evans',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0579'})
SET j.nombre = 'Callum Harris',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0580'})
SET j.nombre = 'Daniel Jackson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0581'})
SET j.nombre = 'Ethan Johnson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0582'})
SET j.nombre = 'George Miller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0583'})
SET j.nombre = 'Harry Mitchell',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0584'})
SET j.nombre = 'Jack Robinson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0585'})
SET j.nombre = 'James Smith',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0586'})
SET j.nombre = 'Liam Taylor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0587'})
SET j.nombre = 'Mason Thompson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0588'})
SET j.nombre = 'Noah Wilson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0589'})
SET j.nombre = 'Oliver Anderson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0590'})
SET j.nombre = 'Samuel Brown',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0591'})
SET j.nombre = 'Thomas Campbell',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-37'})
MERGE (j:Jugador {codigo: 'JUG-0592'})
SET j.nombre = 'William Clark',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0593'})
SET j.nombre = 'Adam Evans',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0594'})
SET j.nombre = 'Benjamin Harris',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0595'})
SET j.nombre = 'Callum Jackson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0596'})
SET j.nombre = 'Daniel Johnson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0597'})
SET j.nombre = 'Ethan Miller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0598'})
SET j.nombre = 'George Mitchell',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0599'})
SET j.nombre = 'Harry Robinson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0600'})
SET j.nombre = 'Jack Smith',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0601'})
SET j.nombre = 'James Taylor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0602'})
SET j.nombre = 'Liam Thompson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0603'})
SET j.nombre = 'Mason Wilson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0604'})
SET j.nombre = 'Noah Anderson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0605'})
SET j.nombre = 'Oliver Brown',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0606'})
SET j.nombre = 'Samuel Campbell',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0607'})
SET j.nombre = 'Thomas Clark',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-38'})
MERGE (j:Jugador {codigo: 'JUG-0608'})
SET j.nombre = 'William Davies',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0609'})
SET j.nombre = 'Ahmed Abbas',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0610'})
SET j.nombre = 'Ali Al-Hassan',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0611'})
SET j.nombre = 'Amir Al-Masri',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0612'})
SET j.nombre = 'Bilal Al-Sayed',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0613'})
SET j.nombre = 'Farid Amrani',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0614'})
SET j.nombre = 'Hamza Benali',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0615'})
SET j.nombre = 'Hassan Farouk',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0616'})
SET j.nombre = 'Ibrahim Haddad',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0617'})
SET j.nombre = 'Karim Khalil',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0618'})
SET j.nombre = 'Khaled Mansour',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0619'})
SET j.nombre = 'Mahmoud Nasser',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0620'})
SET j.nombre = 'Nabil Rahman',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0621'})
SET j.nombre = 'Omar Saidi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0622'})
SET j.nombre = 'Rami Saleh',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0623'})
SET j.nombre = 'Samir Sharif',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-39'})
MERGE (j:Jugador {codigo: 'JUG-0624'})
SET j.nombre = 'Youssef Zaki',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0625'})
SET j.nombre = 'Ahmed Al-Hassan',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0626'})
SET j.nombre = 'Ali Al-Masri',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0627'})
SET j.nombre = 'Amir Al-Sayed',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0628'})
SET j.nombre = 'Bilal Amrani',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0629'})
SET j.nombre = 'Farid Benali',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0630'})
SET j.nombre = 'Hamza Farouk',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0631'})
SET j.nombre = 'Hassan Haddad',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0632'})
SET j.nombre = 'Ibrahim Khalil',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0633'})
SET j.nombre = 'Karim Mansour',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0634'})
SET j.nombre = 'Khaled Nasser',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0635'})
SET j.nombre = 'Mahmoud Rahman',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0636'})
SET j.nombre = 'Nabil Saidi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0637'})
SET j.nombre = 'Omar Saleh',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0638'})
SET j.nombre = 'Rami Sharif',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0639'})
SET j.nombre = 'Samir Zaki',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-40'})
MERGE (j:Jugador {codigo: 'JUG-0640'})
SET j.nombre = 'Youssef Abbas',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0641'})
SET j.nombre = 'Ahmed Al-Masri',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0642'})
SET j.nombre = 'Ali Al-Sayed',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0643'})
SET j.nombre = 'Amir Amrani',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0644'})
SET j.nombre = 'Bilal Benali',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0645'})
SET j.nombre = 'Farid Farouk',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0646'})
SET j.nombre = 'Hamza Haddad',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0647'})
SET j.nombre = 'Hassan Khalil',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0648'})
SET j.nombre = 'Ibrahim Mansour',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0649'})
SET j.nombre = 'Karim Nasser',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0650'})
SET j.nombre = 'Khaled Rahman',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0651'})
SET j.nombre = 'Mahmoud Saidi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0652'})
SET j.nombre = 'Nabil Saleh',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0653'})
SET j.nombre = 'Omar Sharif',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0654'})
SET j.nombre = 'Rami Zaki',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0655'})
SET j.nombre = 'Samir Abbas',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-41'})
MERGE (j:Jugador {codigo: 'JUG-0656'})
SET j.nombre = 'Youssef Al-Hassan',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0657'})
SET j.nombre = 'Ahmed Al-Sayed',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0658'})
SET j.nombre = 'Ali Amrani',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0659'})
SET j.nombre = 'Amir Benali',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0660'})
SET j.nombre = 'Bilal Farouk',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0661'})
SET j.nombre = 'Farid Haddad',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0662'})
SET j.nombre = 'Hamza Khalil',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0663'})
SET j.nombre = 'Hassan Mansour',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0664'})
SET j.nombre = 'Ibrahim Nasser',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0665'})
SET j.nombre = 'Karim Rahman',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0666'})
SET j.nombre = 'Khaled Saidi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0667'})
SET j.nombre = 'Mahmoud Saleh',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0668'})
SET j.nombre = 'Nabil Sharif',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0669'})
SET j.nombre = 'Omar Zaki',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0670'})
SET j.nombre = 'Rami Abbas',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0671'})
SET j.nombre = 'Samir Al-Hassan',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-42'})
MERGE (j:Jugador {codigo: 'JUG-0672'})
SET j.nombre = 'Youssef Al-Masri',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0673'})
SET j.nombre = 'Abdou Ba',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0674'})
SET j.nombre = 'Adebayo Camara',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0675'})
SET j.nombre = 'Amadou Diallo',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0676'})
SET j.nombre = 'Chinedu Diop',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0677'})
SET j.nombre = 'Emmanuel Doumbia',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0678'})
SET j.nombre = 'Fadil Keita',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0679'})
SET j.nombre = 'Idrissa Konaté',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0680'})
SET j.nombre = 'Ismael Mensah',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0681'})
SET j.nombre = 'Kofi Mokoena',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0682'})
SET j.nombre = 'Kwame Ndoye',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0683'})
SET j.nombre = 'Mamadou N\'Komo',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0684'})
SET j.nombre = 'Moussa Okafor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0685'})
SET j.nombre = 'Samuel Ouattara',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0686'})
SET j.nombre = 'Sékou Sissoko',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0687'})
SET j.nombre = 'Tunde Traoré',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-43'})
MERGE (j:Jugador {codigo: 'JUG-0688'})
SET j.nombre = 'Yaya Yeboah',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0689'})
SET j.nombre = 'Abdou Camara',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0690'})
SET j.nombre = 'Adebayo Diallo',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0691'})
SET j.nombre = 'Amadou Diop',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0692'})
SET j.nombre = 'Chinedu Doumbia',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0693'})
SET j.nombre = 'Emmanuel Keita',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0694'})
SET j.nombre = 'Fadil Konaté',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0695'})
SET j.nombre = 'Idrissa Mensah',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0696'})
SET j.nombre = 'Ismael Mokoena',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0697'})
SET j.nombre = 'Kofi Ndoye',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0698'})
SET j.nombre = 'Kwame N\'Komo',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0699'})
SET j.nombre = 'Mamadou Okafor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0700'})
SET j.nombre = 'Moussa Ouattara',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0701'})
SET j.nombre = 'Samuel Sissoko',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0702'})
SET j.nombre = 'Sékou Traoré',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0703'})
SET j.nombre = 'Tunde Yeboah',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-44'})
MERGE (j:Jugador {codigo: 'JUG-0704'})
SET j.nombre = 'Yaya Ba',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0705'})
SET j.nombre = 'Abdou Diallo',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0706'})
SET j.nombre = 'Adebayo Diop',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0707'})
SET j.nombre = 'Amadou Doumbia',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0708'})
SET j.nombre = 'Chinedu Keita',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0709'})
SET j.nombre = 'Emmanuel Konaté',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0710'})
SET j.nombre = 'Fadil Mensah',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0711'})
SET j.nombre = 'Idrissa Mokoena',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0712'})
SET j.nombre = 'Ismael Ndoye',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0713'})
SET j.nombre = 'Kofi N\'Komo',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0714'})
SET j.nombre = 'Kwame Okafor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0715'})
SET j.nombre = 'Mamadou Ouattara',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0716'})
SET j.nombre = 'Moussa Sissoko',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0717'})
SET j.nombre = 'Samuel Traoré',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0718'})
SET j.nombre = 'Sékou Yeboah',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0719'})
SET j.nombre = 'Tunde Ba',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-45'})
MERGE (j:Jugador {codigo: 'JUG-0720'})
SET j.nombre = 'Yaya Camara',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0721'})
SET j.nombre = 'Abdou Diop',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0722'})
SET j.nombre = 'Adebayo Doumbia',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0723'})
SET j.nombre = 'Amadou Keita',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0724'})
SET j.nombre = 'Chinedu Konaté',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0725'})
SET j.nombre = 'Emmanuel Mensah',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0726'})
SET j.nombre = 'Fadil Mokoena',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0727'})
SET j.nombre = 'Idrissa Ndoye',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0728'})
SET j.nombre = 'Ismael N\'Komo',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0729'})
SET j.nombre = 'Kofi Okafor',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0730'})
SET j.nombre = 'Kwame Ouattara',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0731'})
SET j.nombre = 'Mamadou Sissoko',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0732'})
SET j.nombre = 'Moussa Traoré',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0733'})
SET j.nombre = 'Samuel Yeboah',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0734'})
SET j.nombre = 'Sékou Ba',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0735'})
SET j.nombre = 'Tunde Camara',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-46'})
MERGE (j:Jugador {codigo: 'JUG-0736'})
SET j.nombre = 'Yaya Diallo',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0737'})
SET j.nombre = 'Abdou Doumbia',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0738'})
SET j.nombre = 'Adebayo Keita',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0739'})
SET j.nombre = 'Amadou Konaté',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0740'})
SET j.nombre = 'Chinedu Mensah',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0741'})
SET j.nombre = 'Emmanuel Mokoena',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0742'})
SET j.nombre = 'Fadil Ndoye',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0743'})
SET j.nombre = 'Idrissa N\'Komo',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0744'})
SET j.nombre = 'Ismael Okafor',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0745'})
SET j.nombre = 'Kofi Ouattara',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0746'})
SET j.nombre = 'Kwame Sissoko',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0747'})
SET j.nombre = 'Mamadou Traoré',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0748'})
SET j.nombre = 'Moussa Yeboah',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0749'})
SET j.nombre = 'Samuel Ba',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0750'})
SET j.nombre = 'Sékou Camara',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0751'})
SET j.nombre = 'Tunde Diallo',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-47'})
MERGE (j:Jugador {codigo: 'JUG-0752'})
SET j.nombre = 'Yaya Diop',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0753'})
SET j.nombre = 'Abdou Keita',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0754'})
SET j.nombre = 'Adebayo Konaté',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0755'})
SET j.nombre = 'Amadou Mensah',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0756'})
SET j.nombre = 'Chinedu Mokoena',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0757'})
SET j.nombre = 'Emmanuel Ndoye',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0758'})
SET j.nombre = 'Fadil N\'Komo',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0759'})
SET j.nombre = 'Idrissa Okafor',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0760'})
SET j.nombre = 'Ismael Ouattara',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0761'})
SET j.nombre = 'Kofi Sissoko',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0762'})
SET j.nombre = 'Kwame Traoré',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0763'})
SET j.nombre = 'Mamadou Yeboah',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0764'})
SET j.nombre = 'Moussa Ba',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0765'})
SET j.nombre = 'Samuel Camara',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0766'})
SET j.nombre = 'Sékou Diallo',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0767'})
SET j.nombre = 'Tunde Diop',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-48'})
MERGE (j:Jugador {codigo: 'JUG-0768'})
SET j.nombre = 'Yaya Doumbia',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0769'})
SET j.nombre = 'Abdou Konaté',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0770'})
SET j.nombre = 'Adebayo Mensah',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0771'})
SET j.nombre = 'Amadou Mokoena',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0772'})
SET j.nombre = 'Chinedu Ndoye',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0773'})
SET j.nombre = 'Emmanuel N\'Komo',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0774'})
SET j.nombre = 'Fadil Okafor',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0775'})
SET j.nombre = 'Idrissa Ouattara',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0776'})
SET j.nombre = 'Ismael Sissoko',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0777'})
SET j.nombre = 'Kofi Traoré',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0778'})
SET j.nombre = 'Kwame Yeboah',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0779'})
SET j.nombre = 'Mamadou Ba',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0780'})
SET j.nombre = 'Moussa Camara',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0781'})
SET j.nombre = 'Samuel Diallo',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0782'})
SET j.nombre = 'Sékou Diop',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0783'})
SET j.nombre = 'Tunde Doumbia',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-49'})
MERGE (j:Jugador {codigo: 'JUG-0784'})
SET j.nombre = 'Yaya Keita',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0785'})
SET j.nombre = 'Abdou Mensah',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0786'})
SET j.nombre = 'Adebayo Mokoena',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0787'})
SET j.nombre = 'Amadou Ndoye',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0788'})
SET j.nombre = 'Chinedu N\'Komo',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0789'})
SET j.nombre = 'Emmanuel Okafor',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0790'})
SET j.nombre = 'Fadil Ouattara',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0791'})
SET j.nombre = 'Idrissa Sissoko',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0792'})
SET j.nombre = 'Ismael Traoré',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0793'})
SET j.nombre = 'Kofi Yeboah',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0794'})
SET j.nombre = 'Kwame Ba',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0795'})
SET j.nombre = 'Mamadou Camara',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0796'})
SET j.nombre = 'Moussa Diallo',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0797'})
SET j.nombre = 'Samuel Diop',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0798'})
SET j.nombre = 'Sékou Doumbia',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0799'})
SET j.nombre = 'Tunde Keita',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-50'})
MERGE (j:Jugador {codigo: 'JUG-0800'})
SET j.nombre = 'Yaya Konaté',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0801'})
SET j.nombre = 'Daichi Abe',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0802'})
SET j.nombre = 'Haruto Endo',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0803'})
SET j.nombre = 'Hiroki Fujita',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0804'})
SET j.nombre = 'Kaito Hayashi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0805'})
SET j.nombre = 'Kazuki Ito',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0806'})
SET j.nombre = 'Kenji Kobayashi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0807'})
SET j.nombre = 'Kota Matsumoto',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0808'})
SET j.nombre = 'Naoki Mori',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0809'})
SET j.nombre = 'Ren Nakamura',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0810'})
SET j.nombre = 'Riku Saito',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0811'})
SET j.nombre = 'Ryota Sasaki',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0812'})
SET j.nombre = 'Sota Suzuki',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0813'})
SET j.nombre = 'Takumi Takahashi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0814'})
SET j.nombre = 'Yuki Tanaka',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0815'})
SET j.nombre = 'Yuma Watanabe',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-51'})
MERGE (j:Jugador {codigo: 'JUG-0816'})
SET j.nombre = 'Yuya Yamamoto',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0817'})
SET j.nombre = 'Do-yun Choi',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0818'})
SET j.nombre = 'Hyun-woo Han',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0819'})
SET j.nombre = 'Ji-ho Hong',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0820'})
SET j.nombre = 'Jun-ho Hwang',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0821'})
SET j.nombre = 'Min-jae Jang',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0822'})
SET j.nombre = 'Min-jun Jeong',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0823'})
SET j.nombre = 'Seong-ho Jo',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0824'})
SET j.nombre = 'Si-woo Kang',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0825'})
SET j.nombre = 'Sung-min Kim',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0826'})
SET j.nombre = 'Tae-hyun Kwon',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0827'})
SET j.nombre = 'Woo-jin Lee',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0828'})
SET j.nombre = 'Ye-jun Lim',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0829'})
SET j.nombre = 'Yong-ho Park',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0830'})
SET j.nombre = 'Yu-jin Seo',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0831'})
SET j.nombre = 'Yun-seo Shin',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-52'})
MERGE (j:Jugador {codigo: 'JUG-0832'})
SET j.nombre = 'Jin-woo Yoon',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0833'})
SET j.nombre = 'Bo Bai',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0834'})
SET j.nombre = 'Chen Chen',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0835'})
SET j.nombre = 'Hao Gao',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0836'})
SET j.nombre = 'Jian Huang',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0837'})
SET j.nombre = 'Jun Li',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0838'})
SET j.nombre = 'Kai Lin',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0839'})
SET j.nombre = 'Lei Liu',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0840'})
SET j.nombre = 'Ming Ma',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0841'})
SET j.nombre = 'Peng Sun',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0842'})
SET j.nombre = 'Qiang Wang',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0843'})
SET j.nombre = 'Tao Wu',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0844'})
SET j.nombre = 'Wei Xu',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0845'})
SET j.nombre = 'Xiang Yang',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0846'})
SET j.nombre = 'Yang Zhang',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0847'})
SET j.nombre = 'Yong Zhao',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-53'})
MERGE (j:Jugador {codigo: 'JUG-0848'})
SET j.nombre = 'Zhen Zhou',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0849'})
SET j.nombre = 'Adam Harris',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0850'})
SET j.nombre = 'Benjamin Jackson',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0851'})
SET j.nombre = 'Callum Johnson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0852'})
SET j.nombre = 'Daniel Miller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0853'})
SET j.nombre = 'Ethan Mitchell',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0854'})
SET j.nombre = 'George Robinson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0855'})
SET j.nombre = 'Harry Smith',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0856'})
SET j.nombre = 'Jack Taylor',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0857'})
SET j.nombre = 'James Thompson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0858'})
SET j.nombre = 'Liam Wilson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0859'})
SET j.nombre = 'Mason Anderson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0860'})
SET j.nombre = 'Noah Brown',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0861'})
SET j.nombre = 'Oliver Campbell',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0862'})
SET j.nombre = 'Samuel Clark',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0863'})
SET j.nombre = 'Thomas Davies',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-54'})
MERGE (j:Jugador {codigo: 'JUG-0864'})
SET j.nombre = 'William Evans',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0865'})
SET j.nombre = 'Alireza Ahmadi',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0866'})
SET j.nombre = 'Amir Azadi',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0867'})
SET j.nombre = 'Arman Ebrahimi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0868'})
SET j.nombre = 'Ashkan Farhadi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0869'})
SET j.nombre = 'Ehsan Ghasemi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0870'})
SET j.nombre = 'Farhad Hosseini',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0871'})
SET j.nombre = 'Hamid Jafari',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0872'})
SET j.nombre = 'Kian Karimi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0873'})
SET j.nombre = 'Mahdi Mahmoudi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0874'})
SET j.nombre = 'Mehdi Moradi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0875'})
SET j.nombre = 'Milad Rahimi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0876'})
SET j.nombre = 'Omid Rezaei',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0877'})
SET j.nombre = 'Reza Rostami',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0878'})
SET j.nombre = 'Saman Sadeghi',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0879'})
SET j.nombre = 'Saeed Sharifi',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-55'})
MERGE (j:Jugador {codigo: 'JUG-0880'})
SET j.nombre = 'Vahid Yazdani',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0881'})
SET j.nombre = 'Ahmed Amrani',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0882'})
SET j.nombre = 'Ali Benali',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0883'})
SET j.nombre = 'Amir Farouk',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0884'})
SET j.nombre = 'Bilal Haddad',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0885'})
SET j.nombre = 'Farid Khalil',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0886'})
SET j.nombre = 'Hamza Mansour',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0887'})
SET j.nombre = 'Hassan Nasser',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0888'})
SET j.nombre = 'Ibrahim Rahman',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0889'})
SET j.nombre = 'Karim Saidi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0890'})
SET j.nombre = 'Khaled Saleh',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0891'})
SET j.nombre = 'Mahmoud Sharif',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0892'})
SET j.nombre = 'Nabil Zaki',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0893'})
SET j.nombre = 'Omar Abbas',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0894'})
SET j.nombre = 'Rami Al-Hassan',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0895'})
SET j.nombre = 'Samir Al-Masri',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-56'})
MERGE (j:Jugador {codigo: 'JUG-0896'})
SET j.nombre = 'Youssef Al-Sayed',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0897'})
SET j.nombre = 'Ahmed Benali',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0898'})
SET j.nombre = 'Ali Farouk',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0899'})
SET j.nombre = 'Amir Haddad',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0900'})
SET j.nombre = 'Bilal Khalil',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0901'})
SET j.nombre = 'Farid Mansour',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0902'})
SET j.nombre = 'Hamza Nasser',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0903'})
SET j.nombre = 'Hassan Rahman',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0904'})
SET j.nombre = 'Ibrahim Saidi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0905'})
SET j.nombre = 'Karim Saleh',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0906'})
SET j.nombre = 'Khaled Sharif',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0907'})
SET j.nombre = 'Mahmoud Zaki',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0908'})
SET j.nombre = 'Nabil Abbas',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0909'})
SET j.nombre = 'Omar Al-Hassan',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0910'})
SET j.nombre = 'Rami Al-Masri',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0911'})
SET j.nombre = 'Samir Al-Sayed',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-57'})
MERGE (j:Jugador {codigo: 'JUG-0912'})
SET j.nombre = 'Youssef Amrani',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0913'})
SET j.nombre = 'Ahmed Farouk',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0914'})
SET j.nombre = 'Ali Haddad',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0915'})
SET j.nombre = 'Amir Khalil',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0916'})
SET j.nombre = 'Bilal Mansour',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0917'})
SET j.nombre = 'Farid Nasser',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0918'})
SET j.nombre = 'Hamza Rahman',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0919'})
SET j.nombre = 'Hassan Saidi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0920'})
SET j.nombre = 'Ibrahim Saleh',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0921'})
SET j.nombre = 'Karim Sharif',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0922'})
SET j.nombre = 'Khaled Zaki',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0923'})
SET j.nombre = 'Mahmoud Abbas',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0924'})
SET j.nombre = 'Nabil Al-Hassan',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0925'})
SET j.nombre = 'Omar Al-Masri',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0926'})
SET j.nombre = 'Rami Al-Sayed',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0927'})
SET j.nombre = 'Samir Amrani',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-58'})
MERGE (j:Jugador {codigo: 'JUG-0928'})
SET j.nombre = 'Youssef Benali',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0929'})
SET j.nombre = 'Ahmet Çelik',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0930'})
SET j.nombre = 'Ali Demir',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0931'})
SET j.nombre = 'Arda Erdoğan',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0932'})
SET j.nombre = 'Ayberk Güneş',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0933'})
SET j.nombre = 'Burak Kaya',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0934'})
SET j.nombre = 'Can Kılıç',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0935'})
SET j.nombre = 'Emre Koç',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0936'})
SET j.nombre = 'Eren Özcan',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0937'})
SET j.nombre = 'Hakan Polat',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0938'})
SET j.nombre = 'Kerem Şahin',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0939'})
SET j.nombre = 'Mehmet Tekin',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0940'})
SET j.nombre = 'Mert Toprak',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0941'})
SET j.nombre = 'Oğuz Yıldırım',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0942'})
SET j.nombre = 'Onur Yılmaz',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0943'})
SET j.nombre = 'Selim Zengin',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-59'})
MERGE (j:Jugador {codigo: 'JUG-0944'})
SET j.nombre = 'Yusuf Aydın',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0945'})
SET j.nombre = 'Ahmed Haddad',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0946'})
SET j.nombre = 'Ali Khalil',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0947'})
SET j.nombre = 'Amir Mansour',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0948'})
SET j.nombre = 'Bilal Nasser',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0949'})
SET j.nombre = 'Farid Rahman',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0950'})
SET j.nombre = 'Hamza Saidi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0951'})
SET j.nombre = 'Hassan Saleh',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0952'})
SET j.nombre = 'Ibrahim Sharif',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0953'})
SET j.nombre = 'Karim Zaki',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0954'})
SET j.nombre = 'Khaled Abbas',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0955'})
SET j.nombre = 'Mahmoud Al-Hassan',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0956'})
SET j.nombre = 'Nabil Al-Masri',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0957'})
SET j.nombre = 'Omar Al-Sayed',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0958'})
SET j.nombre = 'Rami Amrani',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0959'})
SET j.nombre = 'Samir Benali',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-60'})
MERGE (j:Jugador {codigo: 'JUG-0960'})
SET j.nombre = 'Youssef Farouk',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0961'})
SET j.nombre = 'Adam Jackson',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0962'})
SET j.nombre = 'Benjamin Johnson',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0963'})
SET j.nombre = 'Callum Miller',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0964'})
SET j.nombre = 'Daniel Mitchell',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0965'})
SET j.nombre = 'Ethan Robinson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0966'})
SET j.nombre = 'George Smith',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0967'})
SET j.nombre = 'Harry Taylor',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0968'})
SET j.nombre = 'Jack Thompson',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0969'})
SET j.nombre = 'James Wilson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0970'})
SET j.nombre = 'Liam Anderson',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0971'})
SET j.nombre = 'Mason Brown',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0972'})
SET j.nombre = 'Noah Campbell',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0973'})
SET j.nombre = 'Oliver Clark',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0974'})
SET j.nombre = 'Samuel Davies',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0975'})
SET j.nombre = 'Thomas Evans',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-61'})
MERGE (j:Jugador {codigo: 'JUG-0976'})
SET j.nombre = 'William Harris',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0977'})
SET j.nombre = 'Adrien Blanc',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0978'})
SET j.nombre = 'Antoine Dubois',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0979'})
SET j.nombre = 'Baptiste Dupont',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0980'})
SET j.nombre = 'Clément Fontaine',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0981'})
SET j.nombre = 'Enzo Fournier',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0982'})
SET j.nombre = 'Étienne Laurent',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0983'})
SET j.nombre = 'Hugo Lefèvre',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0984'})
SET j.nombre = 'Jules Leroy',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0985'})
SET j.nombre = 'Laurent Martin',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0986'})
SET j.nombre = 'Léo Mercier',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0987'})
SET j.nombre = 'Lucas Moreau',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0988'})
SET j.nombre = 'Mathis Petit',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0989'})
SET j.nombre = 'Nathan Robert',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0990'})
SET j.nombre = 'Rémi Simon',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0991'})
SET j.nombre = 'Théo Bernard',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-62'})
MERGE (j:Jugador {codigo: 'JUG-0992'})
SET j.nombre = 'Victor Bertrand',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-0993'})
SET j.nombre = 'Aisea Bale',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-0994'})
SET j.nombre = 'Ben Cakau',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-0995'})
SET j.nombre = 'Caleb Derenalagi',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-0996'})
SET j.nombre = 'Eroni Koroibete',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-0997'})
SET j.nombre = 'Filipo Mata',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-0998'})
SET j.nombre = 'Ioane Nacuqu',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-0999'})
SET j.nombre = 'Jone Nakarawa',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1000'})
SET j.nombre = 'Joshua Qera',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1001'})
SET j.nombre = 'Kelepi Ravouvou',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1002'})
SET j.nombre = 'Laisenia Ratu',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1003'})
SET j.nombre = 'Malakai Serevi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1004'})
SET j.nombre = 'Pita Tuisova',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1005'})
SET j.nombre = 'Samuela Tuwai',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1006'})
SET j.nombre = 'Semi Vakatawa',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1007'})
SET j.nombre = 'Sione Vunipola',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-63'})
MERGE (j:Jugador {codigo: 'JUG-1008'})
SET j.nombre = 'Tevita Waqa',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1009'})
SET j.nombre = 'Aisea Cakau',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1010'})
SET j.nombre = 'Ben Derenalagi',
    j.posicion = 'Arquero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1011'})
SET j.nombre = 'Caleb Koroibete',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1012'})
SET j.nombre = 'Eroni Mata',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1013'})
SET j.nombre = 'Filipo Nacuqu',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1014'})
SET j.nombre = 'Ioane Nakarawa',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1015'})
SET j.nombre = 'Jone Qera',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1016'})
SET j.nombre = 'Joshua Ravouvou',
    j.posicion = 'Defensor'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1017'})
SET j.nombre = 'Kelepi Ratu',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1018'})
SET j.nombre = 'Laisenia Serevi',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1019'})
SET j.nombre = 'Malakai Tuisova',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1020'})
SET j.nombre = 'Pita Tuwai',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1021'})
SET j.nombre = 'Samuela Vakatawa',
    j.posicion = 'Mediocampista'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1022'})
SET j.nombre = 'Semi Vunipola',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1023'})
SET j.nombre = 'Sione Waqa',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

MERGE (e:Equipo {codigo: 'EQ-64'})
MERGE (j:Jugador {codigo: 'JUG-1024'})
SET j.nombre = 'Tevita Bale',
    j.posicion = 'Delantero'
MERGE (j)-[:PERTENECE_A]->(e);

