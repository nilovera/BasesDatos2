const sistema = ["admin", "config", "local"];

db.adminCommand({ listDatabases: 1 }).databases
  .filter(base => !sistema.includes(base.name))
  .forEach(base => {
    const actual = db.getSiblingDB(base.name);

    print("\n================================");
    print("BASE: " + base.name);
    print("================================");

    actual.getCollectionNames().sort().forEach(nombre => {
      const coleccion = actual.getCollection(nombre);
      const informacion = actual.getCollectionInfos({ name: nombre })[0];

      print("\nCOLECCION: " + nombre);
      print("DOCUMENTOS: " + coleccion.countDocuments({}));

      print("\nVALIDADOR:");
      printjson(informacion.options);

      print("\nINDICES:");
      printjson(coleccion.getIndexes());

      print("\nDOCUMENTO DE MUESTRA:");
      printjson(coleccion.findOne());
    });
  });
