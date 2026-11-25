// CRUD acotado a NodoDemo. No modifica el catalogo oficial.
CREATE (n:NodoDemo {id: 'DEMO-MANUAL', nombre: 'Creado', estado: 'NUEVO'});

MATCH (n:NodoDemo {id: 'DEMO-MANUAL'})
RETURN n.id AS id, n.nombre AS nombre, n.estado AS estado;

MATCH (n:NodoDemo {id: 'DEMO-MANUAL'})
SET n.nombre = 'Actualizado', n.estado = 'VALIDADO'
RETURN n.id AS id, n.nombre AS nombre, n.estado AS estado;

MATCH (n:NodoDemo {id: 'DEMO-MANUAL'})
DELETE n;
