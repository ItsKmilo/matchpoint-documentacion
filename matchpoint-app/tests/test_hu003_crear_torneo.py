"""HU003 · Crear torneo."""
from unittest import mock

from tests.base import MatchPointTest

T = {"nombre": "Copa Interfacultades 2026", "deporte": "Fútbol", "fecha_inicio": "2026-12-01", "fecha_fin": "2026-12-20", "descripcion": "Torneo entre facultades"}


class HU003(MatchPointTest):
    def setUp(self):
        super().setUp()
        self.login()

    def test_paso1_formulario(self):
        html = self.html(self.client.get("/admin/torneos/nuevo"))
        for campo in ("nombre", "deporte", "fecha_inicio", "fecha_fin", "descripcion"):
            self.assertIn(f'name="{campo}"', html)

    def test_paso2_fecha_fin_no_anterior(self):
        html = self.html(self.client.post("/admin/torneos/nuevo", data={**T, "fecha_fin": "2026-11-25"}))
        self.assertIn("La fecha de fin no puede ser anterior a la de inicio.", html)
        html = self.html(self.client.post("/admin/torneos/nuevo", data={**T, "nombre": ""}))
        self.assertIn("El nombre del torneo es obligatorio.", html)
        self.assertEqual(self.count("SELECT count(*) FROM torneos"), 0)

    def test_paso3_advierte_duplicado(self):
        self.client.post("/admin/torneos/nuevo", data=T)
        html = self.html(self.client.post("/admin/torneos/nuevo", data=T))
        self.assertIn("Ya existe «Copa Interfacultades 2026» en esas fechas.", html)
        self.assertEqual(self.count("SELECT count(*) FROM torneos"), 1)

    def test_paso4_queda_programado_en_la_lista(self):
        self.client.post("/admin/torneos/nuevo", data=T)
        self.assertEqual(self.con.execute("SELECT estado FROM torneos").fetchone()[0], "Programado")
        self.assertIn("Copa Interfacultades 2026", self.html(self.client.get("/admin/torneos")))

    def test_paso5_cancelar(self):
        self.assertIn('href="/admin/torneos">Cancelar', self.html(self.client.get("/admin/torneos/nuevo")))
        self.assertEqual(self.count("SELECT count(*) FROM torneos"), 0)

    def test_paso6_error_vuelve_a_la_lista(self):
        with mock.patch("matchpoint.services.crear_torneo", side_effect=RuntimeError("fallo")):
            r = self.client.post("/admin/torneos/nuevo", data=T)
        self.assertIn("/admin/torneos", r.headers["Location"])
        self.assertIn("No se pudo guardar el torneo.", self.html(self.client.get("/admin/torneos")))
