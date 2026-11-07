"""HU014 · Publicar resultado oficial."""
from matchpoint import services as S
from tests.base import Sprint2Test


class HU014(Sprint2Test):
    def setUp(self):
        super().setUp()
        S.cerrar_evento(self.con, self.eid)
        self.login()

    def test_paso1_formulario_de_marcador(self):
        html = self.html(self.client.get(f"/admin/eventos/{self.eid}/resultado"))
        self.assertIn('name="goles_local"', html)
        self.assertIn('name="goles_visitante"', html)

    def test_paso2_solo_admin(self):
        self.logout()
        self.login("laura.gomez", "demo123")
        self.assertEqual(self.client.post(f"/admin/eventos/{self.eid}/resultado", data={"goles_local": 2, "goles_visitante": 1, "confirmado": "1"}).status_code, 403)

    def test_paso3_confirmacion_antes_de_publicar(self):
        html = self.html(self.client.post(f"/admin/eventos/{self.eid}/resultado", data={"goles_local": 2, "goles_visitante": 1}))
        self.assertIn("Publicar resultado oficial", html)
        self.assertIn("Opción ganadora: Local", html)
        self.assertIsNone(S.obtener_evento(self.con, self.eid)["resultado"])

    def test_paso4_queda_finalizado(self):
        self.client.post(f"/admin/eventos/{self.eid}/resultado", data={"goles_local": 2, "goles_visitante": 1, "confirmado": "1"})
        ev = S.obtener_evento(self.con, self.eid)
        self.assertEqual((ev["estado"], ev["resultado"]), ("Finalizado", "LOCAL"))

    def test_paso5_evento_abierto(self):
        e2 = self.evento(self.tid, dias=5)
        self.assertIn("primero debe cerrarse", self.html(self.client.get(f"/admin/eventos/{e2}/resultado")))

    def test_paso6_no_se_sobrescribe(self):
        S.publicar_resultado(self.con, self.eid, 2, 1)
        with self.assertRaises(S.ValidationError):
            S.publicar_resultado(self.con, self.eid, 0, 0)
        self.assertEqual(S.obtener_evento(self.con, self.eid)["resultado"], "LOCAL")
