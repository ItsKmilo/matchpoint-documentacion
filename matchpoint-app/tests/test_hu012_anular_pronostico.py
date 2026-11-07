"""HU012 · Anular pronóstico."""
from matchpoint import services as S
from tests.base import Sprint2Test


class HU012(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.login("laura.gomez", "demo123")

    def test_paso1_valida_que_el_evento_siga_abierto(self):
        self.assertEqual(self.client.get(f"/pronosticos/{self.p_laura}/anular").status_code, 200)

    def test_paso2_dialogo_con_reintegro(self):
        html = self.html(self.client.get(f"/pronosticos/{self.p_laura}/anular"))
        self.assertIn("¿Anular pronóstico?", html)
        self.assertIn("Se reintegrarán 100 créditos", html)

    def test_paso3_queda_anulado_y_reintegra(self):
        self.client.post(f"/pronosticos/{self.p_laura}/anular")
        self.assertEqual(self.estado_p(self.p_laura), "Anulado")
        self.assertEqual(self.saldo(self.laura), 1000)
        self.assertEqual(self.count("SELECT count(*) FROM movimientos WHERE tipo='REINTEGRO'"), 1)

    def test_paso4_cancelar_no_cambia(self):
        self.assertIn('href="/mis-pronosticos">Mantener', self.html(self.client.get(f"/pronosticos/{self.p_laura}/anular")))
        self.assertEqual(self.estado_p(self.p_laura), "Pendiente")

    def test_paso5_evento_cerrado(self):
        S.cerrar_evento(self.con, self.eid)
        r = self.client.post(f"/pronosticos/{self.p_laura}/anular", follow_redirects=True)
        self.assertIn("porque el evento está cerrado", self.html(r))
        self.assertEqual(self.saldo(self.laura), 900)

    def test_paso6_sin_doble_reintegro(self):
        self.client.post(f"/pronosticos/{self.p_laura}/anular")
        self.client.post(f"/pronosticos/{self.p_laura}/anular")
        self.assertEqual(self.saldo(self.laura), 1000)
        self.assertEqual(self.count("SELECT count(*) FROM movimientos WHERE tipo='REINTEGRO'"), 1)
