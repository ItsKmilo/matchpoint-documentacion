"""HU018 · Consultar transacciones."""
from tests.base import Sprint2Test


class HU018(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.login()

    def test_paso1_lista_movimientos(self):
        html = self.html(self.client.get("/admin/control/transacciones"))
        for t in ("MV-0001", "laura.gomez", "Asignación inicial", "Pronóstico"):
            self.assertIn(t, html)

    def test_paso2_filtros(self):
        html = self.html(self.client.get(f"/admin/control/transacciones?usuario={self.carlos}&tipo=PRONOSTICO&evento={self.eid}"))
        self.assertIn("carlos.ruiz", html)
        self.assertNotIn("<td>laura.gomez</td>", html)

    def test_paso3_detalle_con_origen(self):
        mid = self.con.execute("SELECT id FROM movimientos WHERE tipo='PRONOSTICO' AND usuario_id=?", (self.laura,)).fetchone()[0]
        html = self.html(self.client.get(f"/admin/control/transacciones?id={mid}"))
        self.assertIn(f"P-{self.p_laura:04d}", html)

    def test_paso4_solo_lectura(self):
        self.assertEqual(self.client.post("/admin/control/transacciones").status_code, 405)
        self.assertIn("Solo lectura", self.html(self.client.get("/admin/control/transacciones")))

    def test_paso5_sin_resultados(self):
        self.assertIn("Sin movimientos para los filtros seleccionados.", self.html(self.client.get("/admin/control/transacciones?tipo=AJUSTE")))
