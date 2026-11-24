CONSISTENCY LOCAL_ONE;

SELECT keyspace_name
FROM system_schema.keyspaces
WHERE keyspace_name = 'fixture2030_comments';

SELECT table_name
FROM system_schema.tables
WHERE keyspace_name = 'fixture2030_comments';

