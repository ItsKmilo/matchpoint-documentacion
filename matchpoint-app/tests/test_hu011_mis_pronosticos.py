"""HU011 · Consultar mis pronósticos."""
from tests.base import Sprint2Test


class HU011(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.login("laura.gomez", "demo123")

    def test_paso1_lista_con_datos(self):
        html = self.html(self.client.get("/mis-pronosticos"))
        for t in ("Ingeniería FC vs Derecho United", "Copa UMB 2026", "Local", "100"):
            self.assertIn(t, html)

    def test_paso2_estados(self):
        self.assertIn("Pendiente", self.html(self.client.get("/mis-pronosticos")))
        self.finalizar()
        self.assertIn("Acertado", self.html(self.client.get("/mis-pronosticos")))

    def test_paso3_detalle_con_resultado_y_premio(self):
        self.finalizar()
        html = self.html(self.client.get(f"/mis-pronosticos?id={self.p_laura}"))
        self.assertIn("2 – 1 (Local)", html)
        self.assertIn("+250", html)

    def test_paso4_solo_los_propios(self):
        html = self.html(self.client.get(f"/mis-pronosticos?id={self.p_sofia}"))
        self.assertNotIn("Empate</dd>", html)
        self.assertIn("Selecciona un pronóstico", html)

    def test_paso5_sin_pronosticos(self):
        self.logout()
        self.participante("ana.p", "Ana P")
        self.login("ana.p", "demo123")
        html = self.html(self.client.get("/mis-pronosticos"))
        self.assertIn("Aún no tienes pronósticos.", html)
        self.assertIn("Torneos disponibles", html)
