"""HU004 · Editar torneo."""
from datetime import date, timedelta

from tests.base import MatchPointTest


class HU004(MatchPointTest):
    def setUp(self):
        super().setUp()
        self.login()
        self.tid = self.torneo()

    def form(self, **kw):
        t = self.con.execute("SELECT * FROM torneos WHERE id = ?", (self.tid,)).fetchone()
        d = {"nombre": t["nombre"], "fecha_inicio": t["fecha_inicio"], "fecha_fin": t["fecha_fin"], "descripcion": t["descripcion"]}
        d.update(kw)
        return d

    def test_paso1_carga_datos_actuales(self):
        self.assertIn('value="Copa UMB 2026"', self.html(self.client.get(f"/admin/torneos/{self.tid}/editar")))

    def test_paso2_no_edita_finalizado(self):
        self.con.execute("UPDATE torneos SET estado = 'Finalizado' WHERE id = ?", (self.tid,))
        self.assertIn("no se puede editar", self.html(self.client.get(f"/admin/torneos/{self.tid}/editar")))
        self.client.post(f"/admin/torneos/{self.tid}/editar", data=self.form(nombre="Otro"))
        self.assertEqual(self.con.execute("SELECT nombre FROM torneos").fetchone()[0], "Copa UMB 2026")

    def test_paso3_fechas_deben_cubrir_eventos(self):
        self.evento(self.tid, dias=10)
        corta = (date.today() + timedelta(days=5)).isoformat()
        html = self.html(self.client.post(f"/admin/torneos/{self.tid}/editar", data=self.form(fecha_fin=corta)))
        self.assertIn("Las fechas deben cubrir todos los eventos programados", html)

    def test_paso4_valida_y_actualiza(self):
        html = self.html(self.client.post(f"/admin/torneos/{self.tid}/editar", data=self.form(fecha_fin="2000-01-01")))
        self.assertIn("La fecha de fin no puede ser anterior a la de inicio.", html)
        self.client.post(f"/admin/torneos/{self.tid}/editar", data=self.form(nombre="Copa UMB 2026 · Edición II"))
        self.assertIn("Copa UMB 2026 · Edición II", self.html(self.client.get("/admin/torneos")))

    def test_paso5_cancelar_no_cambia(self):
        self.assertIn('href="/admin/torneos">Cancelar', self.html(self.client.get(f"/admin/torneos/{self.tid}/editar")))
        self.assertEqual(self.con.execute("SELECT nombre FROM torneos").fetchone()[0], "Copa UMB 2026")

    def test_paso6_registra_quien_y_cuando(self):
        self.client.post(f"/admin/torneos/{self.tid}/editar", data=self.form(descripcion="Nueva descripción"))
        c = self.con.execute("SELECT c.*, u.usuario FROM cambios_torneo c JOIN usuarios u ON u.id = c.usuario_id").fetchone()
        self.assertEqual(c["usuario"], "admin")
        self.assertTrue(c["creado_en"])
        self.assertIn("Cambió la descripción", self.html(self.client.get(f"/admin/torneos/{self.tid}/editar")))
