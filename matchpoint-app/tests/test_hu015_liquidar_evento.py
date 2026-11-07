"""HU015 · Liquidar evento y acreditar premios."""
from unittest import mock

from matchpoint import services as S
from tests.base import Sprint2Test


class HU015(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.finalizar(liquidar=False)
        self.login()

    def test_paso1_identifica_acertados(self):
        r = S.resumen_liquidacion(self.con, self.eid)
        self.assertEqual({p["id"] for p in r["ganadores"]}, {self.p_laura, self.p_carlos})

    def test_paso2_resumen_previo(self):
        html = self.html(self.client.get(f"/admin/eventos/{self.eid}/liquidar"))
        for t in ("PRONÓSTICOS", "ACERTADOS", "NO ACERTADOS", "500", "Confirmar liquidación"):
            self.assertIn(t, html)

    def test_paso3_acredita_y_marca(self):
        self.client.post(f"/admin/eventos/{self.eid}/liquidar")
        self.assertEqual(self.saldo(self.laura), 1150)
        self.assertEqual(self.estado_p(self.p_sofia), "No acertado")
        self.assertEqual(self.estado_p(self.p_carlos), "Acertado")

    def test_paso4_movimiento_premio_vinculado(self):
        S.liquidar_evento(self.con, self.eid)
        m = self.con.execute("SELECT * FROM movimientos WHERE tipo='PREMIO' AND usuario_id=?", (self.laura,)).fetchone()
        self.assertEqual((m["valor"], m["origen"], m["evento_id"]), (250, f"P-{self.p_laura:04d}", self.eid))

    def test_paso5_no_duplica_premios(self):
        self.client.post(f"/admin/eventos/{self.eid}/liquidar")
        r = self.client.post(f"/admin/eventos/{self.eid}/liquidar", follow_redirects=True)
        self.assertIn("ya fue liquidado", self.html(r))
        self.assertEqual(self.count("SELECT count(*) FROM movimientos WHERE tipo='PREMIO'"), 2)

    def test_paso6_error_no_deja_abonos_parciales(self):
        real = S._mov
        llamadas = []

        def falla(*a, **k):
            llamadas.append(1)
            if len(llamadas) == 2:
                raise RuntimeError("fallo simulado")
            return real(*a, **k)
        with mock.patch("matchpoint.services._mov", side_effect=falla):
            with self.assertRaises(RuntimeError):
                S.liquidar_evento(self.con, self.eid)
        self.assertEqual(self.saldo(self.laura), 900)
        self.assertEqual(self.count("SELECT count(*) FROM movimientos WHERE tipo='PREMIO'"), 0)
