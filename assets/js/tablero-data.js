/* Tablero del Sprint 1 · se actualiza con cada sesión del equipo. */
window.MATCHPOINT_TABLERO = {
 "sprint": {
  "nombre": "Sprint 1 · Configurar y participar",
  "inicio": "2026-11-02",
  "entrega_avance": "2026-11-03",
  "objetivo": "Tener un recorrido funcional verificable: ingreso por rol, participantes con créditos iniciales, torneos y eventos programados, consulta de eventos y registro de pronósticos con descuento seguro de créditos.",
  "roles": {
   "Scrum Master": "Santiago Solano",
   "Product Owner": "Diego Romero (propuesto, por confirmar)",
   "Backend": "Maicol Rubiano",
   "Frontend": "Diego Romero",
   "DBA": "Camilo Bastidas"
  },
  "codigo": "matchpoint-app/"
 },
 "historias": [
  {
   "id": "HU001",
   "name": "Iniciar sesión",
   "sp": 5,
   "priority": "Must",
   "owner": "Maicol Rubiano",
   "estado": "En revisión",
   "pruebas": 6,
   "pasos": 6,
   "mockup": "assets/img/mockups/HU001.png",
   "test": "matchpoint-app/tests/test_hu001_"
  },
  {
   "id": "HU002",
   "name": "Registrar participante",
   "sp": 3,
   "priority": "Must",
   "owner": "Diego Romero",
   "estado": "En revisión",
   "pruebas": 6,
   "pasos": 6,
   "mockup": "assets/img/mockups/HU002.png",
   "test": "matchpoint-app/tests/test_hu002_"
  },
  {
   "id": "HU003",
   "name": "Crear torneo",
   "sp": 3,
   "priority": "Must",
   "owner": "Diego Romero",
   "estado": "En revisión",
   "pruebas": 6,
   "pasos": 6,
   "mockup": "assets/img/mockups/HU003.png",
   "test": "matchpoint-app/tests/test_hu003_"
  },
  {
   "id": "HU004",
   "name": "Editar torneo",
   "sp": 3,
   "priority": "Should",
   "owner": "Diego Romero",
   "estado": "En revisión",
   "pruebas": 6,
   "pasos": 6,
   "mockup": "assets/img/mockups/HU004.png",
   "test": "matchpoint-app/tests/test_hu004_"
  },
  {
   "id": "HU005",
   "name": "Eliminar torneo",
   "sp": 3,
   "priority": "Should",
   "owner": "Camilo Bastidas",
   "estado": "En revisión",
   "pruebas": 6,
   "pasos": 6,
   "mockup": "assets/img/mockups/HU005.png",
   "test": "matchpoint-app/tests/test_hu005_"
  },
  {
   "id": "HU006",
   "name": "Programar evento",
   "sp": 5,
   "priority": "Must",
   "owner": "Maicol Rubiano",
   "estado": "En revisión",
   "pruebas": 6,
   "pasos": 6,
   "mockup": "assets/img/mockups/HU006.png",
   "test": "matchpoint-app/tests/test_hu006_"
  },
  {
   "id": "HU007",
   "name": "Consultar torneos y eventos",
   "sp": 3,
   "priority": "Must",
   "owner": "Diego Romero",
   "estado": "En revisión",
   "pruebas": 5,
   "pasos": 5,
   "mockup": "assets/img/mockups/HU007.png",
   "test": "matchpoint-app/tests/test_hu007_"
  },
  {
   "id": "HU008",
   "name": "Registrar pronóstico",
   "sp": 8,
   "priority": "Must",
   "owner": "Maicol Rubiano",
   "estado": "En revisión",
   "pruebas": 8,
   "pasos": 7,
   "mockup": "assets/img/mockups/HU008.png",
   "test": "matchpoint-app/tests/test_hu008_"
  },
  {
   "id": "HU009",
   "name": "Asignar créditos iniciales",
   "sp": 3,
   "priority": "Must",
   "owner": "Camilo Bastidas",
   "estado": "En revisión",
   "pruebas": 5,
   "pasos": 5,
   "mockup": "assets/img/mockups/HU009.png",
   "test": "matchpoint-app/tests/test_hu009_"
  },
  {
   "id": "HU010",
   "name": "Consultar saldo y movimientos",
   "sp": 3,
   "priority": "Must",
   "owner": "Diego Romero",
   "estado": "En revisión",
   "pruebas": 5,
   "pasos": 5,
   "mockup": "assets/img/mockups/HU010.png",
   "test": "matchpoint-app/tests/test_hu010_"
  }
 ],
 "entradas": [
  {
   "fecha": "2026-11-02",
   "tipo": "Planeación",
   "rol": "Backlog",
   "texto": "Se toma para el Sprint 1 el compromiso de HU001 a HU010 (39 SP), estimados en el Product Backlog."
  },
  {
   "fecha": "2026-11-02",
   "tipo": "Avance técnico",
   "rol": "Desarrollo",
   "texto": "Implementadas HU001 a HU010 en Python (Flask + SQLite) con 59 pruebas automáticas, una por paso del criterio de aceptación. Todas pasan. Las 10 historias pasan a «En revisión»."
  }
 ],
 "sesiones": [
  {
   "n": 1,
   "fecha": "2026-11-02",
   "tipo": "Planeación del Sprint 1 y refinamiento",
   "estado": "Programada",
   "duracion": "30 min",
   "agenda": [
    "SM abre la sesión y confirma roles (PO incluido).",
    "PO presenta el objetivo del Sprint 1 y el orden de las 10 HU.",
    "El equipo confirma estimaciones (SP) y responsables.",
    "Demo corta de la app: iniciar sesión, crear torneo y registrar pronóstico.",
    "Se acuerdan los siguientes pasos y la fecha de la revisión."
   ],
   "asistentes": [],
   "acuerdos": [],
   "evidencia": ""
  },
  {
   "n": 2,
   "fecha": "2026-11-03",
   "tipo": "Revisión de avance con el Product Owner",
   "estado": "Programada",
   "duracion": "20 min",
   "agenda": [
    "Cada responsable muestra sus HU funcionando paso a paso contra su mockup.",
    "PO acepta o rechaza cada HU (Terminado / vuelve a En progreso).",
    "SM registra impedimentos y el avance (SP terminados).",
    "Se actualiza el tablero antes de la entrega."
   ],
   "asistentes": [],
   "acuerdos": [],
   "evidencia": ""
  }
 ]
};
