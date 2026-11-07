# MatchPoint · Sprints 1 y 2 (Python + Flask)

Implementación del **Sprint 1 · Configurar y participar** (HU001 a HU010) y del **Sprint 2 · Resolver y controlar** (HU011 a HU020) del proyecto MatchPoint.
Los créditos son **virtuales**: no tienen valor monetario ni pueden retirarse.

| HU | Historia | Dónde está en el código | Pruebas |
|---|---|---|---|
| HU001 | Iniciar sesión | `matchpoint/auth.py` | `tests/test_hu001_iniciar_sesion.py` |
| HU002 | Registrar participante | `admin.py` · `services.registrar_participante` | `tests/test_hu002_registrar_participante.py` |
| HU003 | Crear torneo | `admin.py` · `services.crear_torneo` | `tests/test_hu003_crear_torneo.py` |
| HU004 | Editar torneo | `admin.py` · `services.editar_torneo` | `tests/test_hu004_editar_torneo.py` |
| HU005 | Eliminar torneo | `admin.py` · `services.eliminar_torneo` | `tests/test_hu005_eliminar_torneo.py` |
| HU006 | Programar evento | `admin.py` · `services.crear_evento` | `tests/test_hu006_programar_evento.py` |
| HU007 | Consultar torneos y eventos | `participante.py` · `services.torneos_activos` | `tests/test_hu007_consultar_torneos.py` |
| HU008 | Registrar pronóstico | `participante.py` · `services.registrar_pronostico` | `tests/test_hu008_registrar_pronostico.py` |
| HU009 | Asignar créditos iniciales | `services.asignar_creditos_iniciales` | `tests/test_hu009_creditos_iniciales.py` |
| HU010 | Consultar saldo y movimientos | `participante.py` · `services.verificar_saldo` | `tests/test_hu010_saldo_movimientos.py` |
| HU011 | Consultar mis pronósticos | `participante.py` · `services.mis_pronosticos` | `tests/test_hu011_mis_pronosticos.py` |
| HU012 | Anular pronóstico | `participante.py` · `services.anular_pronostico` | `tests/test_hu012_anular_pronostico.py` |
| HU013 | Cerrar recepción de pronósticos | `admin.py` · `services.cerrar_evento` | `tests/test_hu013_cerrar_pronosticos.py` |
| HU014 | Publicar resultado oficial | `admin.py` · `services.publicar_resultado` | `tests/test_hu014_publicar_resultado.py` |
| HU015 | Liquidar evento y acreditar premios | `admin.py` · `services.liquidar_evento` | `tests/test_hu015_liquidar_evento.py` |
| HU016 | Corregir resultado publicado | `admin.py` · `services.corregir_resultado` | `tests/test_hu016_corregir_resultado.py` |
| HU017 | Ajustar créditos autorizados | `admin.py` · `services.ajustar_creditos` | `tests/test_hu017_ajustar_creditos.py` |
| HU018 | Consultar transacciones | `admin.py` · `services.transacciones` | `tests/test_hu018_transacciones.py` |
| HU019 | Conciliar saldos | `admin.py` · `services.conciliar` | `tests/test_hu019_conciliar_saldos.py` |
| HU020 | Generar reporte del torneo | `admin.py` · `services.reporte_torneo` | `tests/test_hu020_reporte_torneo.py` |

Cada archivo de pruebas tiene **una prueba por paso** del criterio de aceptación de la HU (`test_paso1_…`, `test_paso2_…`).

## Cómo ejecutarlo (macOS / Linux)

```bash
cd matchpoint-app
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py --demo               # carga datos de ejemplo la primera vez
```

Abre **http://127.0.0.1:5000** en el navegador.

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin` | `admin123` |
| Participante (demo) | `laura.gomez` | `demo123` |
| Participante (demo) | `carlos.ruiz` | `demo123` |

`python run.py --reset` borra la base local (`instance/matchpoint.sqlite`) y la crea de nuevo.

## Cómo correr las pruebas

```bash
python -m unittest discover -s tests -t . -v
```

Resultado esperado: **114 pruebas OK** (59 del Sprint 1 y 55 del Sprint 2).

> Si ya tenías una base creada en el Sprint 1, la app agrega sola las columnas nuevas al arrancar. Para empezar limpio: `python run.py --reset --demo`.

## Estructura

```text
matchpoint-app/
├── run.py                  arranque (--demo, --reset)
├── requirements.txt        Flask
├── matchpoint/
│   ├── __init__.py         crea la app Flask
│   ├── schema.sql          tablas SQLite con reglas (saldo >= 0, un pronóstico por evento, etc.)
│   ├── db.py               conexión y transacciones atómicas
│   ├── services.py         reglas de negocio de cada HU
│   ├── auth.py             HU001: sesión y permisos por rol
│   ├── admin.py            HU002–HU006, HU009, HU013–HU020 (administrador y control)
│   ├── participante.py     HU007, HU008, HU010–HU012 (vistas del participante)
│   ├── templates/          pantallas basadas en los mockups
│   └── static/style.css
└── tests/                  una prueba por paso de cada HU
```

## Reglas que el código garantiza

- Los permisos se validan en el servidor: un participante recibe **403** si intenta una función de administrador.
- Pronóstico y descuento de créditos ocurren en **una sola transacción**; si algo falla no se aplica nada.
- Una solicitud repetida (doble clic o reintento) **no cobra dos veces** (`solicitud_id` único).
- El saldo nunca queda negativo (restricción `CHECK (saldo >= 0)` y validación previa).
- La asignación inicial de créditos solo puede existir **una vez** por participante.
- El saldo mostrado siempre se compara con la suma de los movimientos.
- Anular un pronóstico solo es posible antes del cierre y nunca reintegra dos veces.
- Un resultado publicado no se sobrescribe: se corrige con motivo, historial y movimientos compensatorios.
- Liquidar un evento dos veces no duplica premios; si algo falla, no se aplica ningún abono.
