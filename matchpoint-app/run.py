"""Arranque de MatchPoint.

    python run.py            -> inicia el servidor en http://127.0.0.1:5000
    python run.py --demo     -> carga datos de ejemplo (si la base está vacía) e inicia
    python run.py --reset    -> borra la base local y la vuelve a crear
"""
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from matchpoint import create_app, services as S
from matchpoint.db import connect, init_db

app = create_app()


def cargar_demo():
    con = connect(app.config["DATABASE"])
    if con.execute("SELECT count(*) FROM torneos").fetchone()[0]:
        print("La base ya tiene datos; no se cargó la demo.")
        return
    hoy = date.today()
    for nombre, correo, usuario in [("Laura Gómez", "laura.gomez@umb.edu.co", "laura.gomez"),
                                    ("Carlos Ruiz", "carlos.ruiz@umb.edu.co", "carlos.ruiz")]:
        S.registrar_participante(con, nombre, correo, usuario, "demo123")
    t1 = S.crear_torneo(con, "Copa UMB 2026", "Fútbol", hoy.isoformat(), (hoy + timedelta(days=30)).isoformat(), "Copa institucional de fútbol.")
    S.crear_torneo(con, "Liga Interna Sistemas", "Baloncesto", (hoy + timedelta(days=10)).isoformat(), (hoy + timedelta(days=40)).isoformat())
    base = datetime.combine(hoy, datetime.min.time())
    for d, l, v in [(3, "Ingeniería FC", "Derecho United"), (5, "Medicina", "Arquitectura"), (8, "Sistemas", "Psicología")]:
        ini = base + timedelta(days=d, hours=18)
        S.crear_evento(con, t1, l, v, ini.strftime("%Y-%m-%dT%H:%M"), (ini - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M"), 100, 250)
    # Sprint 2: un evento con pronósticos ya cerrado, listo para publicar resultado, liquidar y corregir en la demo
    ids = [r[0] for r in con.execute("SELECT id FROM eventos ORDER BY inicio")]
    laura = con.execute("SELECT id FROM usuarios WHERE usuario = 'laura.gomez'").fetchone()[0]
    carlos = con.execute("SELECT id FROM usuarios WHERE usuario = 'carlos.ruiz'").fetchone()[0]
    S.registrar_pronostico(con, laura, ids[2], "LOCAL", "demo-1")
    S.registrar_pronostico(con, carlos, ids[2], "EMPATE", "demo-2")
    S.registrar_pronostico(con, carlos, ids[1], "VISITANTE", "demo-3")
    S.cerrar_evento(con, ids[2])
    print("Demo cargada: participantes laura.gomez / carlos.ruiz (clave demo123), 2 torneos y 3 eventos "
          "(Sistemas vs Psicología ya cerrado con 2 pronósticos, listo para publicar resultado y liquidar).")


if __name__ == "__main__":
    if "--reset" in sys.argv:
        Path(app.config["DATABASE"]).unlink(missing_ok=True)
        init_db(app.config["DATABASE"])
        print("Base de datos reiniciada.")
    if "--demo" in sys.argv:
        cargar_demo()
    print("MatchPoint en http://127.0.0.1:5000  ·  administrador: admin / admin123")
    app.run(debug=True)
