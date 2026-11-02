# MatchPoint · Guía de sesiones del Sprint 1

**Scrum Master:** Santiago Solano · **Product Owner (propuesto):** Diego Romero · **Equipo:** Maicol Rubiano, Diego Romero, Camilo Bastidas

La entrega «Avance sprint 1» pide el tablero con las historias estimadas y el avance, el seguimiento del Scrum Master y del Product Owner, y el reporte de sesiones con entradas en distintas fechas. Para eso hacen **dos sesiones cortas reales** y llenan un acta por cada una (`02_ACTA_PLANTILLA.md`).

## Antes de la primera sesión (5 min, quien comparte pantalla)

1. Abrir `matchpoint-app` y seguir su `README.md` para ejecutarla (`python run.py --demo`).
2. Correr las pruebas: `python -m unittest discover -s tests -t . -v` (deben salir 59 OK).
3. Tener abierto el tablero: https://itskmilo.github.io/matchpoint-documentacion/tablero.html

## Sesión 1 · Hoy 2 de noviembre · Planeación del Sprint 1 (30 min, por Meet/Discord/WhatsApp)

| Min | Quién | Qué se hace |
|---|---|---|
| 0–5 | Scrum Master | Abre la sesión, confirma asistentes y que el Product Owner es Diego (o quien decidan). |
| 5–10 | Product Owner | Presenta el objetivo del Sprint 1 y el orden de prioridad de HU001 a HU010. |
| 10–20 | Equipo | Revisa los puntos (SP) de cada HU y confirma responsables. Si alguien no está de acuerdo con una estimación, se anota el cambio. |
| 20–27 | Quien comparte | Demo corta: iniciar sesión como admin, crear un torneo, programar un evento, entrar como participante y registrar un pronóstico. |
| 27–30 | Scrum Master | Fija la hora de la sesión 2 y anota impedimentos. Toma captura de la reunión como evidencia. |

## Sesión 2 · Mañana 3 de noviembre · Revisión de avance con el PO (20 min)

| Min | Quién | Qué se hace |
|---|---|---|
| 0–12 | Cada responsable | Muestra sus HU funcionando, paso a paso, comparando con su mockup. |
| 12–17 | Product Owner | Acepta cada HU (pasa a **Terminado**) o la devuelve (**En progreso**) diciendo qué falta. |
| 17–20 | Scrum Master | Cuenta los SP terminados, registra impedimentos y pide actualizar el tablero. |

## Después de cada sesión

- Llenar el acta con lo que **realmente** pasó (asistentes, acuerdos, estado de cada HU).
- Pasar el acta a Claude (o editar `assets/js/tablero-data.js` del sitio): la sesión pasa de «Programada» a «Realizada» y las HU aceptadas se mueven a «Terminado».
- Guardar la evidencia: captura de la videollamada o del chat con fecha y hora.

## Qué entregar en Canvas

La URL del tablero: **https://itskmilo.github.io/matchpoint-documentacion/tablero.html**. Ahí están las historias estimadas, el avance, el seguimiento del SM y el PO y el reporte de sesiones. Si la docente pide archivo, adjuntar también las actas en PDF.
