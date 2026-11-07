"""HU017 · Ajustar créditos autorizados."""
from tests.base import Sprint2Test


class HU017(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.login()
        self.url = f"/admin/participantes/{self.laura}/ajustar"

    def test_paso1_formulario(self):
        html = self.html(self.client.get(self.url))
        for t in ('value="ABONO"', 'value="CARGO"', 'name="cantidad"', 'name="motivo"'):
            self.assertIn(t, html)

    def test_paso2_valida_cantidad_y_saldo(self):
        self.assertIn("mayor que cero", self.html(self.client.post(self.url, data={"tipo": "ABONO", "cantidad": "0", "motivo": "x"})))
        self.assertIn("dejaría el saldo en negativo", self.html(self.client.post(self.url, data={"tipo": "CARGO", "cantidad": "5000", "motivo": "x"})))

    def test_paso3_confirmacion_con_saldo_resultante(self):
        html = self.html(self.client.post(self.url, data={"tipo": "ABONO", "cantidad": "150", "motivo": "Compensación"}))
        self.assertIn("Confirmar ajuste", html)
        self.assertIn("1.050", html)
        self.assertEqual(self.saldo(self.laura), 900)

    def test_paso4_registra_ajuste(self):
        self.client.post(self.url, data={"tipo": "ABONO", "cantidad": "150", "motivo": "Compensación", "confirmado": "1"})
        m = self.con.execute("SELECT * FROM movimientos WHERE tipo='AJUSTE'").fetchone()
        self.assertEqual((m["valor"], m["autor_id"]), (150, 1))
        self.assertIn("Compensación", m["detalle"])
        self.assertEqual(self.saldo(self.laura), 1050)

    def test_paso5_cancelar(self):
        self.client.post(self.url, data={"tipo": "ABONO", "cantidad": "150", "motivo": "x"})
        self.assertEqual(self.saldo(self.laura), 900)

    def test_paso6_solo_control(self):
        self.logout()
        self.login("laura.gomez", "demo123")
        self.assertEqual(self.client.post(self.url, data={"tipo": "ABONO", "cantidad": "999", "motivo": "x", "confirmado": "1"}).status_code, 403)
