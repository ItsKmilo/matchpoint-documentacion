"""HU005 · Eliminar torneo."""
from unittest import mock

from tests.base import MatchPointTest


class HU005(MatchPointTest):
    def setUp(self):
        super().setUp()
        self.login()
        self.vacio = self.torneo("Liga Interna Sistemas")
        self.con_eventos = self.torneo("Copa UMB 2026")
        self.evento(self.con_eventos)

    def test_paso1_valida_eventos_asociados(self):
        r = self.client.get(f"/admin/torneos/{self.con_eventos}/eliminar")
        self.assertEqual(r.status_code, 302)

    def test_paso2_dialogo_de_confirmacion(self):
        html = self.html(self.client.get(f"/admin/torneos/{self.vacio}/eliminar"))
        self.assertIn("¿Eliminar torneo?", html)
        self.assertIn("Liga Interna Sistemas", html)

    def test_paso3_al_confirmar_desaparece(self):
        self.client.post(f"/admin/torneos/{self.vacio}/eliminar")
        self.assertNotIn("<b>Liga Interna Sistemas</b>", self.html(self.client.get("/admin/torneos")))

    def test_paso4_cancelar_lo_conserva(self):
        self.assertIn('href="/admin/torneos">Cancelar', self.html(self.client.get(f"/admin/torneos/{self.vacio}/eliminar")))
        self.assertIn("Liga Interna Sistemas", self.html(self.client.get("/admin/torneos")))

    def test_paso5_error_notifica_y_vuelve(self):
        with mock.patch("matchpoint.services.eliminar_torneo", side_effect=RuntimeError("fallo")):
            r = self.client.post(f"/admin/torneos/{self.vacio}/eliminar")
        self.assertIn("/admin/torneos", r.headers["Location"])
        html = self.html(self.client.get("/admin/torneos"))
        self.assertIn("Ocurrió un error al eliminar", html)
        self.assertIn("Liga Interna Sistemas", html)

    def test_paso6_con_eventos_no_se_elimina(self):
        self.client.post(f"/admin/torneos/{self.con_eventos}/eliminar")
        html = self.html(self.client.get("/admin/torneos"))
        self.assertIn("porque el torneo está vinculado a 1 evento", html)
        self.assertEqual(self.count("SELECT count(*) FROM torneos WHERE id = ?", self.con_eventos), 1)
