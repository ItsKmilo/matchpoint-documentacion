"""HU020 · Generar reporte del torneo."""
from datetime import date, timedelta

from tests.base import Sprint2Test


class HU020(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.login()
        self.url = f"/admin/torneos/{self.tid}/reporte"

    def test_paso1_resumen(self):
        self.finalizar()
        html = self.html(self.client.get(self.url))
        for t in ("EVENTOS", "PRONÓSTICOS", "ACIERTOS", "CRÉDITOS USADOS", "PREMIOS", ">300<", ">500<"):
            self.assertIn(t, html)

    def test_paso2_filtro_por_fechas(self):
        lejos = (date.today() + timedelta(days=20)).isoformat()
        self.assertIn("No hay eventos en este rango.", self.html(self.client.get(f"{self.url}?desde={lejos}")))

    def test_paso3_totales_coinciden_con_movimientos(self):
        self.finalizar()
        self.assertIn("Totales verificados", self.html(self.client.get(self.url)))

    def test_paso4_descarga(self):
        self.finalizar()
        r = self.client.get(f"{self.url}?formato=csv")
        self.assertIn("text/csv", r.headers["Content-Type"])
        self.assertIn("Ingeniería FC vs Derecho United", self.html(r))
        self.assertIn("window.print()", self.html(self.client.get(self.url)))

    def test_paso5_sin_eventos_liquidados(self):
        self.assertIn("aún no tiene resultados", self.html(self.client.get(self.url)))
