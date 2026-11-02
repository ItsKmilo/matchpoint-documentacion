"""HU007 · Consultar torneos y eventos."""
from tests.base import MatchPointTest


class HU007(MatchPointTest):
    def setUp(self):
        super().setUp()
        self.uid = self.participante()

    def entrar(self):
        self.login("laura.gomez", "demo123")

    def test_paso1_lista_torneos_activos(self):
        self.torneo("Copa UMB 2026")
        t = self.torneo("Torneo viejo")
        self.con.execute("UPDATE torneos SET estado='Finalizado' WHERE id=?", (t,))
        self.entrar()
        html = self.html(self.client.get("/torneos"))
        self.assertIn("Copa UMB 2026", html)
        self.assertNotIn("Torneo viejo", html)

    def test_paso2_eventos_con_detalle(self):
        tid = self.torneo()
        self.evento(tid, costo=100, premio=250)
        self.entrar()
        html = self.html(self.client.get(f"/torneos?torneo={tid}"))
        for txt in ("Ingeniería FC vs Derecho United", ">100<", ">250<"):
            self.assertIn(txt, html)

    def test_paso3_solo_abiertos_permiten_pronosticar(self):
        tid = self.torneo()
        e1 = self.evento(tid, dias=3)
        e2 = self.evento(tid, dias=4)
        self.con.execute("UPDATE eventos SET estado='Finalizado' WHERE id=?", (e2,))
        self.entrar()
        html = self.html(self.client.get(f"/torneos?torneo={tid}"))
        self.assertIn(f'href="/eventos/{e1}">Pronosticar', html)
        self.assertIn('disabled" aria-disabled="true">Pronosticar', html)

    def test_paso4_filtro_por_estado(self):
        tid = self.torneo()
        self.evento(tid)
        self.entrar()
        self.assertIn("Ingeniería FC", self.html(self.client.get(f"/torneos?torneo={tid}&estado=abiertos")))
        self.assertIn("No hay eventos con ese estado.", self.html(self.client.get(f"/torneos?torneo={tid}&estado=cerrados")))

    def test_paso5_sin_torneos(self):
        self.entrar()
        self.assertIn("No hay torneos disponibles por el momento.", self.html(self.client.get("/torneos")))
