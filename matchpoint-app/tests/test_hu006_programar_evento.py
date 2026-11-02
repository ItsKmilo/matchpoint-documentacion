"""HU006 · Programar evento."""
from datetime import date, datetime, timedelta

from tests.base import MatchPointTest


def dt(dias, h=18, m=0):
    return (datetime.combine(date.today() + timedelta(days=dias), datetime.min.time()) + timedelta(hours=h, minutes=m)).strftime("%Y-%m-%dT%H:%M")


class HU006(MatchPointTest):
    def setUp(self):
        super().setUp()
        self.login()
        self.tid = self.torneo(dias=30)
        self.ok = {"local": "Ingeniería FC", "visitante": "Derecho United", "inicio": dt(5), "cierre": dt(5, 17, 30), "costo": "100", "premio": "250"}

    def post(self, **kw):
        return self.client.post(f"/admin/torneos/{self.tid}/eventos/nuevo", data={**self.ok, **kw})

    def test_paso1_formulario(self):
        html = self.html(self.client.get(f"/admin/torneos/{self.tid}/eventos/nuevo"))
        for c in ("local", "visitante", "inicio", "cierre", "costo", "premio"):
            self.assertIn(f'name="{c}"', html)

    def test_paso2_campos_requeridos(self):
        html = self.html(self.post(local="", costo="0"))
        self.assertIn("El contendiente local es obligatorio.", html)
        self.assertIn("El costo debe ser un número entero mayor que cero.", html)

    def test_paso3_cierre_antes_del_inicio_y_en_rango(self):
        self.assertIn("Debe ser anterior al inicio del encuentro.", self.html(self.post(cierre=dt(5, 18, 30))))
        self.assertIn("Debe estar dentro del rango del torneo", self.html(self.post(inicio=dt(60), cierre=dt(60, 17))))

    def test_paso4_opciones_y_contendientes_distintos(self):
        self.assertIn("El mismo contendiente no puede estar en los dos lados.", self.html(self.post(visitante="ingeniería fc")))
        html = self.html(self.client.get(f"/admin/torneos/{self.tid}/eventos/nuevo"))
        for o in ("Local", "Empate", "Visitante"):
            self.assertIn(o, html)

    def test_paso5_aparece_abierto_en_calendario(self):
        self.post()
        html = self.html(self.client.get(f"/admin/torneos/{self.tid}"))
        self.assertIn("Ingeniería FC vs Derecho United", html)
        self.assertIn("Abierto", html)

    def test_paso6_si_falla_no_guarda(self):
        r = self.post(cierre="")
        self.assertEqual(r.status_code, 400)
        self.assertIn("Corrige los campos marcados", self.html(r))
        self.assertEqual(self.count("SELECT count(*) FROM eventos"), 0)
