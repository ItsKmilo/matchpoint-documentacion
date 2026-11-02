# MatchPoint · Sprint 1 (Python + Flask)

Implementación del **Sprint 1 · Configurar y participar** (HU001 a HU010) del proyecto MatchPoint.
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

Resultado esperado: **59 pruebas OK**.

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
│   ├── admin.py            HU002–HU006, HU009 (vistas del administrador)
│   ├── participante.py     HU007, HU008, HU010 (vistas del participante)
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
