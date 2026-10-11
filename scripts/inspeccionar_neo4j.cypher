RETURN '=== HITO 10 - INSPECCION NEO4J ===' AS resultado;

CALL db.labels()
YIELD label
RETURN label
ORDER BY label;

CALL db.relationshipTypes()
YIELD relationshipType
RETURN relationshipType
ORDER BY relationshipType;

MATCH (n)
UNWIND labels(n) AS etiqueta
RETURN etiqueta, count(*) AS cantidad_nodos
ORDER BY etiqueta;

MATCH ()-[r]->()
RETURN type(r) AS relacion, count(*) AS cantidad
ORDER BY relacion;

MATCH (n)
UNWIND labels(n) AS etiqueta
UNWIND keys(n) AS propiedad
RETURN etiqueta, collect(DISTINCT propiedad) AS propiedades
ORDER BY etiqueta;

SHOW CONSTRAINTS;

SHOW INDEXES;

MATCH (n)
RETURN labels(n) AS etiquetas,
       properties(n) AS propiedades
ORDER BY etiquetas
LIMIT 20;

MATCH (origen)-[r]->(destino)
RETURN labels(origen) AS origen,
       properties(origen) AS propiedades_origen,
       type(r) AS relacion,
       labels(destino) AS destino,
       properties(destino) AS propiedades_destino
LIMIT 20;