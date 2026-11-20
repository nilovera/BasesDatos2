// ======================================================
// Fixture 2030 - Hito 4
// Carga reproducible de Equipos y Jugadores
// ======================================================

db = db.getSiblingDB("fixture2030");


// ======================================================
// 1. DATOS BASE
// ======================================================

// Los nombres de las selecciones y sus confederaciones son reales.
// El ranking se mantiene como un valor sintético y estable del 1 al 64.
// El perfil se utiliza únicamente para generar nombres verosímiles;
// no se almacena en MongoDB.
const selecciones = [
  { nombre: "Argentina", confederacion: "CONMEBOL", perfil: "hispano" },
  { nombre: "Bolivia", confederacion: "CONMEBOL", perfil: "hispano" },
  { nombre: "Brasil", confederacion: "CONMEBOL", perfil: "lusofono" },
  { nombre: "Chile", confederacion: "CONMEBOL", perfil: "hispano" },
  { nombre: "Colombia", confederacion: "CONMEBOL", perfil: "hispano" },
  { nombre: "Ecuador", confederacion: "CONMEBOL", perfil: "hispano" },
  { nombre: "Paraguay", confederacion: "CONMEBOL", perfil: "hispano" },
  { nombre: "Perú", confederacion: "CONMEBOL", perfil: "hispano" },
  { nombre: "Uruguay", confederacion: "CONMEBOL", perfil: "hispano" },
  { nombre: "Venezuela", confederacion: "CONMEBOL", perfil: "hispano" },

  { nombre: "Alemania", confederacion: "UEFA", perfil: "germanico" },
  { nombre: "España", confederacion: "UEFA", perfil: "hispano" },
  { nombre: "Francia", confederacion: "UEFA", perfil: "francofono" },
  { nombre: "Inglaterra", confederacion: "UEFA", perfil: "anglo" },
  { nombre: "Italia", confederacion: "UEFA", perfil: "italiano" },
  { nombre: "Portugal", confederacion: "UEFA", perfil: "lusofono" },
  { nombre: "Países Bajos", confederacion: "UEFA", perfil: "germanico" },
  { nombre: "Bélgica", confederacion: "UEFA", perfil: "francofono" },
  { nombre: "Croacia", confederacion: "UEFA", perfil: "eslavo" },
  { nombre: "Suiza", confederacion: "UEFA", perfil: "germanico" },
  { nombre: "Dinamarca", confederacion: "UEFA", perfil: "nordico" },
  { nombre: "Serbia", confederacion: "UEFA", perfil: "eslavo" },
  { nombre: "Austria", confederacion: "UEFA", perfil: "germanico" },
  { nombre: "Polonia", confederacion: "UEFA", perfil: "eslavo" },
  { nombre: "Ucrania", confederacion: "UEFA", perfil: "eslavo" },
  { nombre: "Noruega", confederacion: "UEFA", perfil: "nordico" },
  { nombre: "Suecia", confederacion: "UEFA", perfil: "nordico" },
  { nombre: "Turquía", confederacion: "UEFA", perfil: "turco" },
  { nombre: "Escocia", confederacion: "UEFA", perfil: "anglo" },
  { nombre: "República Checa", confederacion: "UEFA", perfil: "eslavo" },

  { nombre: "Canadá", confederacion: "CONCACAF", perfil: "anglo" },
  { nombre: "Estados Unidos", confederacion: "CONCACAF", perfil: "anglo" },
  { nombre: "México", confederacion: "CONCACAF", perfil: "hispano" },
  { nombre: "Costa Rica", confederacion: "CONCACAF", perfil: "hispano" },
  { nombre: "Panamá", confederacion: "CONCACAF", perfil: "hispano" },
  { nombre: "Honduras", confederacion: "CONCACAF", perfil: "hispano" },
  { nombre: "Jamaica", confederacion: "CONCACAF", perfil: "anglo" },
  { nombre: "Trinidad y Tobago", confederacion: "CONCACAF", perfil: "anglo" },

  { nombre: "Marruecos", confederacion: "CAF", perfil: "arabe" },
  { nombre: "Argelia", confederacion: "CAF", perfil: "arabe" },
  { nombre: "Túnez", confederacion: "CAF", perfil: "arabe" },
  { nombre: "Egipto", confederacion: "CAF", perfil: "arabe" },
  { nombre: "Senegal", confederacion: "CAF", perfil: "africano" },
  { nombre: "Nigeria", confederacion: "CAF", perfil: "africano" },
  { nombre: "Ghana", confederacion: "CAF", perfil: "africano" },
  { nombre: "Camerún", confederacion: "CAF", perfil: "africano" },
  { nombre: "Costa de Marfil", confederacion: "CAF", perfil: "africano" },
  { nombre: "Sudáfrica", confederacion: "CAF", perfil: "africano" },
  { nombre: "Mali", confederacion: "CAF", perfil: "africano" },
  { nombre: "República Democrática del Congo", confederacion: "CAF", perfil: "africano" },

  { nombre: "Japón", confederacion: "AFC", perfil: "japones" },
  { nombre: "Corea del Sur", confederacion: "AFC", perfil: "coreano" },
  { nombre: "China", confederacion: "AFC", perfil: "chino" },
  { nombre: "Australia", confederacion: "AFC", perfil: "anglo" },
  { nombre: "Irán", confederacion: "AFC", perfil: "persa" },
  { nombre: "Arabia Saudita", confederacion: "AFC", perfil: "arabe" },
  { nombre: "Catar", confederacion: "AFC", perfil: "arabe" },
  { nombre: "Irak", confederacion: "AFC", perfil: "arabe" },
  { nombre: "Uzbekistán", confederacion: "AFC", perfil: "turco" },
  { nombre: "Emiratos Árabes Unidos", confederacion: "AFC", perfil: "arabe" },

  { nombre: "Nueva Zelanda", confederacion: "OFC", perfil: "anglo" },
  { nombre: "Nueva Caledonia", confederacion: "OFC", perfil: "francofono" },
  { nombre: "Fiyi", confederacion: "OFC", perfil: "pacifico" },
  { nombre: "Islas Salomón", confederacion: "OFC", perfil: "pacifico" }
];

const perfilesNombres = {
  hispano: {
    nombres: [
      "Alejandro", "Bruno", "Carlos", "Diego",
      "Emiliano", "Facundo", "Gabriel", "Joaquín",
      "Lautaro", "Mateo", "Nicolás", "Ramiro",
      "Santiago", "Tomás", "Valentín", "Martín"
    ],
    apellidos: [
      "García", "Fernández", "González", "Rodríguez",
      "López", "Martínez", "Sánchez", "Pérez",
      "Romero", "Díaz", "Torres", "Álvarez",
      "Ruiz", "Herrera", "Castro", "Silva"
    ]
  },
  lusofono: {
    nombres: [
      "André", "Bruno", "Caio", "Diogo",
      "Eduardo", "Fábio", "Gabriel", "Henrique",
      "João", "Leonardo", "Lucas", "Mateus",
      "Miguel", "Rafael", "Tiago", "Vinícius"
    ],
    apellidos: [
      "Almeida", "Barbosa", "Carvalho", "Costa",
      "Fernandes", "Ferreira", "Gomes", "Lima",
      "Martins", "Mendes", "Moreira", "Oliveira",
      "Pereira", "Ribeiro", "Rocha", "Santos"
    ]
  },
  germanico: {
    nombres: [
      "Alexander", "Benjamin", "Elias", "Felix",
      "Florian", "Jonas", "Julian", "Leon",
      "Lukas", "Maximilian", "Nico", "Noah",
      "Sebastian", "Simon", "Tobias", "Yannick"
    ],
    apellidos: [
      "Bauer", "Becker", "Braun", "Fischer",
      "Hartmann", "Hoffmann", "Keller", "Klein",
      "Koch", "Krüger", "Lehmann", "Meyer",
      "Richter", "Schneider", "Wagner", "Weber"
    ]
  },
  francofono: {
    nombres: [
      "Adrien", "Antoine", "Baptiste", "Clément",
      "Enzo", "Étienne", "Hugo", "Jules",
      "Laurent", "Léo", "Lucas", "Mathis",
      "Nathan", "Rémi", "Théo", "Victor"
    ],
    apellidos: [
      "Bernard", "Bertrand", "Blanc", "Dubois",
      "Dupont", "Fontaine", "Fournier", "Laurent",
      "Lefèvre", "Leroy", "Martin", "Mercier",
      "Moreau", "Petit", "Robert", "Simon"
    ]
  },
  anglo: {
    nombres: [
      "Adam", "Benjamin", "Callum", "Daniel",
      "Ethan", "George", "Harry", "Jack",
      "James", "Liam", "Mason", "Noah",
      "Oliver", "Samuel", "Thomas", "William"
    ],
    apellidos: [
      "Anderson", "Brown", "Campbell", "Clark",
      "Davies", "Evans", "Harris", "Jackson",
      "Johnson", "Miller", "Mitchell", "Robinson",
      "Smith", "Taylor", "Thompson", "Wilson"
    ]
  },
  italiano: {
    nombres: [
      "Alessandro", "Andrea", "Davide", "Federico",
      "Francesco", "Gabriele", "Giacomo", "Giovanni",
      "Leonardo", "Lorenzo", "Luca", "Marco",
      "Matteo", "Riccardo", "Simone", "Tommaso"
    ],
    apellidos: [
      "Bianchi", "Colombo", "Conti", "De Luca",
      "Esposito", "Ferrari", "Gallo", "Greco",
      "Lombardi", "Mancini", "Marino", "Moretti",
      "Ricci", "Romano", "Rossi", "Villa"
    ]
  },
  eslavo: {
    nombres: [
      "Aleksandar", "Andrija", "Bohdan", "Dario",
      "Ivan", "Jakub", "Luka", "Marko",
      "Matej", "Milan", "Nikola", "Oleksandr",
      "Pavel", "Petar", "Tomas", "Viktor"
    ],
    apellidos: [
      "Horvat", "Jovanović", "Kovač", "Kowalski",
      "Marković", "Miletić", "Novak", "Nowak",
      "Petrović", "Popović", "Shevchenko", "Sokolov",
      "Stanić", "Vuković", "Zieliński", "Živković"
    ]
  },
  nordico: {
    nombres: [
      "Anders", "Axel", "Bjørn", "Elias",
      "Emil", "Erik", "Gustav", "Henrik",
      "Isak", "Johan", "Kasper", "Magnus",
      "Mikkel", "Oskar", "Søren", "Viktor"
    ],
    apellidos: [
      "Andersen", "Berg", "Dahl", "Eriksen",
      "Hansen", "Jensen", "Kristensen", "Larsen",
      "Lindberg", "Lund", "Nielsen", "Olsen",
      "Pedersen", "Svensson", "Sørensen", "Vik"
    ]
  },
  turco: {
    nombres: [
      "Ahmet", "Ali", "Arda", "Ayberk",
      "Burak", "Can", "Emre", "Eren",
      "Hakan", "Kerem", "Mehmet", "Mert",
      "Oğuz", "Onur", "Selim", "Yusuf"
    ],
    apellidos: [
      "Aydın", "Çelik", "Demir", "Erdoğan",
      "Güneş", "Kaya", "Kılıç", "Koç",
      "Özcan", "Polat", "Şahin", "Tekin",
      "Toprak", "Yıldırım", "Yılmaz", "Zengin"
    ]
  },
  arabe: {
    nombres: [
      "Ahmed", "Ali", "Amir", "Bilal",
      "Farid", "Hamza", "Hassan", "Ibrahim",
      "Karim", "Khaled", "Mahmoud", "Nabil",
      "Omar", "Rami", "Samir", "Youssef"
    ],
    apellidos: [
      "Abbas", "Al-Hassan", "Al-Masri", "Al-Sayed",
      "Amrani", "Benali", "Farouk", "Haddad",
      "Khalil", "Mansour", "Nasser", "Rahman",
      "Saidi", "Saleh", "Sharif", "Zaki"
    ]
  },
  africano: {
    nombres: [
      "Abdou", "Adebayo", "Amadou", "Chinedu",
      "Emmanuel", "Fadil", "Idrissa", "Ismael",
      "Kofi", "Kwame", "Mamadou", "Moussa",
      "Samuel", "Sékou", "Tunde", "Yaya"
    ],
    apellidos: [
      "Ba", "Camara", "Diallo", "Diop",
      "Doumbia", "Keita", "Konaté", "Mensah",
      "Mokoena", "Ndoye", "N'Komo", "Okafor",
      "Ouattara", "Sissoko", "Traoré", "Yeboah"
    ]
  },
  japones: {
    nombres: [
      "Daichi", "Haruto", "Hiroki", "Kaito",
      "Kazuki", "Kenji", "Kota", "Naoki",
      "Ren", "Riku", "Ryota", "Sota",
      "Takumi", "Yuki", "Yuma", "Yuya"
    ],
    apellidos: [
      "Abe", "Endo", "Fujita", "Hayashi",
      "Ito", "Kobayashi", "Matsumoto", "Mori",
      "Nakamura", "Saito", "Sasaki", "Suzuki",
      "Takahashi", "Tanaka", "Watanabe", "Yamamoto"
    ]
  },
  coreano: {
    nombres: [
      "Do-yun", "Hyun-woo", "Ji-ho", "Jun-ho",
      "Min-jae", "Min-jun", "Seong-ho", "Si-woo",
      "Sung-min", "Tae-hyun", "Woo-jin", "Ye-jun",
      "Yong-ho", "Yu-jin", "Yun-seo", "Jin-woo"
    ],
    apellidos: [
      "Choi", "Han", "Hong", "Hwang",
      "Jang", "Jeong", "Jo", "Kang",
      "Kim", "Kwon", "Lee", "Lim",
      "Park", "Seo", "Shin", "Yoon"
    ]
  },
  chino: {
    nombres: [
      "Bo", "Chen", "Hao", "Jian",
      "Jun", "Kai", "Lei", "Ming",
      "Peng", "Qiang", "Tao", "Wei",
      "Xiang", "Yang", "Yong", "Zhen"
    ],
    apellidos: [
      "Bai", "Chen", "Gao", "Huang",
      "Li", "Lin", "Liu", "Ma",
      "Sun", "Wang", "Wu", "Xu",
      "Yang", "Zhang", "Zhao", "Zhou"
    ]
  },
  persa: {
    nombres: [
      "Alireza", "Amir", "Arman", "Ashkan",
      "Ehsan", "Farhad", "Hamid", "Kian",
      "Mahdi", "Mehdi", "Milad", "Omid",
      "Reza", "Saman", "Saeed", "Vahid"
    ],
    apellidos: [
      "Ahmadi", "Azadi", "Ebrahimi", "Farhadi",
      "Ghasemi", "Hosseini", "Jafari", "Karimi",
      "Mahmoudi", "Moradi", "Rahimi", "Rezaei",
      "Rostami", "Sadeghi", "Sharifi", "Yazdani"
    ]
  },
  pacifico: {
    nombres: [
      "Aisea", "Ben", "Caleb", "Eroni",
      "Filipo", "Ioane", "Jone", "Joshua",
      "Kelepi", "Laisenia", "Malakai", "Pita",
      "Samuela", "Semi", "Sione", "Tevita"
    ],
    apellidos: [
      "Bale", "Cakau", "Derenalagi", "Koroibete",
      "Mata", "Nacuqu", "Nakarawa", "Qera",
      "Ravouvou", "Ratu", "Serevi", "Tuisova",
      "Tuwai", "Vakatawa", "Vunipola", "Waqa"
    ]
  }
};

const posicionesPlantel = [
  "Arquero", "Arquero",
  "Defensor", "Defensor", "Defensor", "Defensor", "Defensor", "Defensor",
  "Mediocampista", "Mediocampista", "Mediocampista", "Mediocampista", "Mediocampista",
  "Delantero", "Delantero", "Delantero"
];

if (selecciones.length !== 64) {
  throw new Error("La lista debe contener exactamente 64 selecciones.");
}

Object.entries(perfilesNombres).forEach(([perfil, datos]) => {
  if (datos.nombres.length !== 16 || datos.apellidos.length !== 16) {
    throw new Error("El perfil " + perfil + " debe tener 16 nombres y 16 apellidos.");
  }
});


// ======================================================
// 2. LIMPIEZA DE REGISTROS TEMPORALES
// ======================================================

// No se borran colecciones ni volúmenes. Los documentos principales
// se actualizan por sus mismos IDs mediante upsert.
db.jugadores.deleteOne({ _id: "JUG-TEST" });
db.equipos.deleteOne({ _id: "EQ-TEST" });


// ======================================================
// 3. CARGA DE 64 EQUIPOS
// ======================================================

const equiposOps = selecciones.map((seleccion, indice) => {
  const equipoId = "EQ-" + String(indice + 1).padStart(2, "0");

  return {
    updateOne: {
      filter: { _id: equipoId },
      update: {
        $set: {
          nombre: seleccion.nombre,
          confederacion: seleccion.confederacion,
          ranking: indice + 1
        }
      },
      upsert: true
    }
  };
});

db.equipos.bulkWrite(equiposOps);
print("64 equipos procesados.");


// ======================================================
// 4. CARGA DE 1.024 JUGADORES
// ======================================================

const contadorPorPerfil = {};
const nombresGenerados = new Set();
const jugadoresOps = [];
let jugadorNumero = 1;

selecciones.forEach((seleccion, indiceEquipo) => {
  const equipoId = "EQ-" + String(indiceEquipo + 1).padStart(2, "0");
  const perfil = perfilesNombres[seleccion.perfil];

  if (!perfil) {
    throw new Error("No existe el perfil de nombres: " + seleccion.perfil);
  }

  if (contadorPorPerfil[seleccion.perfil] === undefined) {
    contadorPorPerfil[seleccion.perfil] = 0;
  }

  for (let indicePlantel = 0; indicePlantel < 16; indicePlantel++) {
    const jugadorId = "JUG-" + String(jugadorNumero).padStart(4, "0");
    const contadorPerfil = contadorPorPerfil[seleccion.perfil];

    // Multiplicar por 17 recorre las 256 combinaciones posibles sin
    // repetirlas dentro de un mismo perfil de nombres.
    const combinacion = (contadorPerfil * 17) % 256;
    const indiceNombre = combinacion % 16;
    const indiceApellido = Math.floor(combinacion / 16);
    const nombreCompleto =
      perfil.nombres[indiceNombre] + " " + perfil.apellidos[indiceApellido];

    if (nombresGenerados.has(nombreCompleto)) {
      throw new Error("Se generó un nombre duplicado: " + nombreCompleto);
    }

    nombresGenerados.add(nombreCompleto);

    // Fechas sintéticas y estables: jugadores de 19 a 37 años en 2030.
    const anio = 1993 + ((jugadorNumero * 7) % 19);
    const mes = 1 + ((jugadorNumero * 5) % 12);
    const dia = 1 + ((jugadorNumero * 11) % 28);

    jugadoresOps.push({
      updateOne: {
        filter: { _id: jugadorId },
        update: {
          $set: {
            nombre: nombreCompleto,
            fecha_nacimiento: new Date(Date.UTC(anio, mes - 1, dia)),
            posicion: posicionesPlantel[indicePlantel],
            equipo_id: equipoId
          }
        },
        upsert: true
      }
    });

    contadorPorPerfil[seleccion.perfil]++;
    jugadorNumero++;
  }
});

if (jugadoresOps.length !== 1024 || nombresGenerados.size !== 1024) {
  throw new Error("La carga debe generar 1.024 jugadores con nombres únicos.");
}

db.jugadores.bulkWrite(jugadoresOps);
print("1024 jugadores procesados.");


// ======================================================
// 5. VERIFICACIONES FINALES
// ======================================================

const cantidadEquipos = db.equipos.countDocuments({
  _id: { $regex: /^EQ-\d{2}$/ }
});

const cantidadJugadores = db.jugadores.countDocuments({
  _id: { $regex: /^JUG-\d{4}$/ }
});

const equiposGenericos = db.equipos.countDocuments({
  nombre: { $regex: /^Equipo \d{2}$/ }
});

const jugadoresGenericos = db.jugadores.countDocuments({
  nombre: { $regex: /^Jugador \d{4}$/ }
});

const jugadoresHuerfanos = db.jugadores.aggregate([
  {
    $match: {
      _id: { $regex: /^JUG-\d{4}$/ }
    }
  },
  {
    $lookup: {
      from: "equipos",
      localField: "equipo_id",
      foreignField: "_id",
      as: "equipo"
    }
  },
  {
    $match: {
      equipo: { $size: 0 }
    }
  },
  {
    $count: "cantidad"
  }
]).toArray();

const plantelesInvalidos = db.jugadores.aggregate([
  {
    $match: {
      _id: { $regex: /^JUG-\d{4}$/ }
    }
  },
  {
    $group: {
      _id: "$equipo_id",
      cantidad: { $sum: 1 }
    }
  },
  {
    $match: {
      cantidad: { $ne: 16 }
    }
  }
]).toArray();

const cantidadHuerfanos =
  jugadoresHuerfanos.length === 0 ? 0 : jugadoresHuerfanos[0].cantidad;

print("Cantidad de equipos principales:", cantidadEquipos);
print("Cantidad de jugadores principales:", cantidadJugadores);
print("Equipos con nombre genérico:", equiposGenericos);
print("Jugadores con nombre genérico:", jugadoresGenericos);
print("Jugadores huérfanos:", cantidadHuerfanos);
print("Planteles con cantidad distinta de 16:", plantelesInvalidos.length);

if (
  cantidadEquipos !== 64 ||
  cantidadJugadores !== 1024 ||
  equiposGenericos !== 0 ||
  jugadoresGenericos !== 0 ||
  cantidadHuerfanos !== 0 ||
  plantelesInvalidos.length !== 0
) {
  throw new Error("La verificación final de la carga no fue superada.");
}

print("Carga reproducible finalizada correctamente.");
