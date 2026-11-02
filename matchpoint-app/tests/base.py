"""Utilidades comunes de las pruebas: cada prueba usa una base SQLite nueva y temporal."""
import os
import tempfile
import unittest
from datetime import date, datetime, timedelta

from matchpoint import create_app, services as S
from matchpoint.db import connect


class MatchPointTest(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        os.unlink(self.db_path)
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path, "SECRET_KEY": "test"})
        self.client = self.app.test_client()
        self.con = connect(self.db_path)

    def tearDown(self):
        self.con.close()
        os.unlink(self.db_path)

    # ---------------------------------------------------------------- ayudas
    def login(self, usuario="admin", clave="admin123"):
        return self.client.post("/ingresar", data={"usuario": usuario, "clave": clave})

    def logout(self):
        return self.client.post("/salir")

    def participante(self, usuario="laura.gomez", nombre="Laura Gómez"):
        return S.registrar_participante(self.con, nombre, f"{usuario}@umb.edu.co", usuario, "demo123")

    def torneo(self, nombre="Copa UMB 2026", dias=30, inicio=None):
        inicio = inicio or date.today()
        return S.crear_torneo(self.con, nombre, "Fútbol", inicio.isoformat(), (inicio + timedelta(days=dias)).isoformat())

    def evento(self, tid, dias=3, costo=100, premio=250, cierre_min=30):
        ini = datetime.combine(date.today() + timedelta(days=dias), datetime.min.time()) + timedelta(hours=18)
        return S.crear_evento(self.con, tid, "Ingeniería FC", "Derecho United", ini.strftime("%Y-%m-%dT%H:%M"),
                              (ini - timedelta(minutes=cierre_min)).strftime("%Y-%m-%dT%H:%M"), costo, premio)

    def html(self, resp):
        return resp.get_data(as_text=True)

    def saldo(self, uid):
        return self.con.execute("SELECT saldo FROM usuarios WHERE id = ?", (uid,)).fetchone()["saldo"]

    def count(self, sql, *args):
        return self.con.execute(sql, args).fetchone()[0]
