"""HU010 · Consultar saldo y movimientos."""
from matchpoint import services as S
from tests.base import MatchPointTest


class HU010(MatchPointTest):
    def setUp(self):
        super().setUp()
        self.uid = self.participante()
        self.otro = self.participante("carlos.ruiz", "Carlos Ruiz")
        tid = self.torneo()
        S.registrar_pronostico(self.con, self.uid, self.evento(tid, costo=100), "LOCAL", "r1")
        S.registrar_pronostico(self.con, self.uid, self.evento(tid, dias=4, costo=80), "EMPATE", "r2")
        self.login("laura.gomez", "demo123")

    def test_paso1_saldo_actualizado(self):
        self.assertIn("820", self.html(self.client.get("/mis-creditos")))

    def test_paso2_movimientos_del_mas_reciente(self):
        html = self.html(self.client.get("/mis-creditos"))
        self.assertLess(html.index("−80") if "−80" in html else html.index("-80"), html.index("+1.000"))

    def test_paso3_signos_y_colores(self):
        html = self.html(self.client.get("/mis-creditos"))
        self.assertIn('class="num neg">-100', html)
        self.assertIn('class="num pos">+1.000', html)

    def test_paso4_saldo_coincide_con_suma(self):
        saldo, suma, ok = S.verificar_saldo(self.con, self.uid)
        self.assertEqual((saldo, suma, ok), (820, 820, True))
        self.assertIn("Saldo verificado", self.html(self.client.get("/mis-creditos")))

    def test_paso5_no_ve_movimientos_ajenos(self):
        r = self.client.get(f"/creditos/{self.otro}")
        self.assertEqual(r.status_code, 403)
        self.assertIn("Acceso no autorizado", self.html(r))
        self.assertNotIn("Carlos Ruiz", self.html(r))
