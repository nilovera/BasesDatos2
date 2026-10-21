// Restricción para los equipos
CREATE CONSTRAINT equipo_codigo IF NOT EXISTS
FOR (e:Equipo)
REQUIRE e.codigo IS UNIQUE;

// Restricción para los jugadores
CREATE CONSTRAINT jugador_codigo IF NOT EXISTS
FOR (j:Jugador)
REQUIRE j.codigo IS UNIQUE;

// Restricción para los partidos
CREATE CONSTRAINT partido_codigo IF NOT EXISTS
FOR (p:Partido)
REQUIRE p.codigo IS UNIQUE;

// Restricción para las sedes
CREATE CONSTRAINT sede_codigo IF NOT EXISTS
FOR (s:Sede)
REQUIRE s.codigo IS UNIQUE;

// Restricción para los eventos
CREATE CONSTRAINT evento_codigo IF NOT EXISTS
FOR (ev:Evento)
REQUIRE ev.codigo IS UNIQUE;

// Verificación
SHOW CONSTRAINTS;