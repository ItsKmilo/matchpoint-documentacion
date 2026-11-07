"""HU019 · Conciliar saldos."""
from tests.base import Sprint2Test


class HU019(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.login()

    def test_paso1_recalcula(self):
        html = self.html(self.client.get("/admin/control/conciliacion?ejecutar=1"))
        self.assertIn("CUENTAS REVISADAS", html)

    def test_paso2_tabla_con_diferencia(self):
        html = self.html(self.client.get("/admin/control/conciliacion?ejecutar=1"))
        for t in ("Saldo registrado", "Saldo calculado", "Diferencia", "Laura Gómez"):
            self.assertIn(t, html)

    def test_paso3_marca_inconsistentes(self):
        self.con.execute("UPDATE usuarios SET saldo = saldo + 50 WHERE id = ?", (self.carlos,))
        html = self.html(self.client.get("/admin/control/conciliacion?ejecutar=1"))
        self.assertIn("Inconsistente", html)
        self.assertIn("Correcto", html)

    def test_paso4_no_modifica_saldos(self):
        self.con.execute("UPDATE usuarios SET saldo = saldo + 50 WHERE id = ?", (self.carlos,))
        self.client.get("/admin/control/conciliacion?ejecutar=1")
        self.assertEqual(self.saldo(self.carlos), 950)

    def test_paso5_csv(self):
        r = self.client.get("/admin/control/conciliacion?formato=csv")
        self.assertIn("text/csv", r.headers["Content-Type"])
        self.assertIn("Laura Gómez,laura.gomez,900,900,0,Correcto", self.html(r))
