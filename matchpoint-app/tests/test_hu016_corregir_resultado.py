"""HU016 · Corregir resultado publicado."""
from matchpoint import services as S
from tests.base import Sprint2Test


class HU016(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.finalizar(2, 1)  # gana Local: Laura y Carlos +250
        self.login()

    def test_paso1_pide_resultado_y_motivo(self):
        html = self.html(self.client.post(f"/admin/eventos/{self.eid}/corregir", data={"goles_local": 1, "goles_visitante": 1, "motivo": ""}))
        self.assertIn("El motivo de la corrección es obligatorio.", html)

    def test_paso2_dialogo_con_impacto(self):
        html = self.html(self.client.post(f"/admin/eventos/{self.eid}/corregir", data={"goles_local": 1, "goles_visitante": 1, "motivo": "Acta"}))
        self.assertIn("Impacto de la corrección", html)
        self.assertIn("2 · −500", html)
        self.assertIn("1 · +250", html)

    def test_paso3_reversion_y_nuevo_premio_sin_borrar(self):
        S.corregir_resultado(self.con, self.eid, 1, 1, 1, "Acta oficial")
        self.assertEqual((self.saldo(self.laura), self.saldo(self.sofia)), (900, 1150))
        self.assertEqual(self.count("SELECT count(*) FROM movimientos WHERE tipo='PREMIO'"), 5)

    def test_paso4_historial(self):
        S.corregir_resultado(self.con, self.eid, 1, 1, 1, "Acta oficial")
        c = self.con.execute("SELECT * FROM correcciones_resultado").fetchone()
        self.assertEqual((c["anterior"], c["nuevo"], c["motivo"]), ("2 – 1 (Local)", "1 – 1 (Empate)", "Acta oficial"))

    def test_paso5_cancelar_no_cambia(self):
        self.client.post(f"/admin/eventos/{self.eid}/corregir", data={"goles_local": 1, "goles_visitante": 1, "motivo": "Acta"})
        self.assertEqual(S.obtener_evento(self.con, self.eid)["resultado"], "LOCAL")
        self.assertEqual(self.saldo(self.laura), 1150)

    def test_paso6_no_aplica_si_queda_saldo_negativo(self):
        self.con.execute("UPDATE usuarios SET saldo = 100 WHERE id = ?", (self.laura,))
        with self.assertRaises(S.ValidationError) as e:
            S.corregir_resultado(self.con, self.eid, 1, 1, 1, "Acta")
        self.assertIn("laura.gomez", str(e.exception))
        self.assertEqual(S.obtener_evento(self.con, self.eid)["resultado"], "LOCAL")
