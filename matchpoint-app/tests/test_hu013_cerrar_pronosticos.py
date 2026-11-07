"""HU013 · Cerrar recepción de pronósticos."""
from matchpoint import services as S
from tests.base import Sprint2Test


class HU013(Sprint2Test):
    def setUp(self):
        super().setUp()
        self.login()

    def test_paso1_cierre_automatico_en_la_fecha_limite(self):
        ev = S.obtener_evento(self.con, self.eid)
        self.assertEqual(S.estado_evento(ev, ahora="2999-01-01T00:00"), "Cerrado")

    def test_paso2_cierre_manual_con_confirmacion(self):
        self.assertIn("¿Cerrar pronósticos?", self.html(self.client.get(f"/admin/eventos/{self.eid}/cerrar")))
        self.client.post(f"/admin/eventos/{self.eid}/cerrar")
        self.assertEqual(S.obtener_evento(self.con, self.eid)["estado"], "Cerrado")

    def test_paso3_rechaza_pronosticos_nuevos(self):
        S.cerrar_evento(self.con, self.eid)
        uid = self.participante("nuevo.p", "Nuevo P")
        with self.assertRaises(S.ValidationError):
            S.registrar_pronostico(self.con, uid, self.eid, "LOCAL", "s-9")

    def test_paso4_muestra_distribucion(self):
        self.assertEqual(S.distribucion(self.con, self.eid), {"LOCAL": 2, "EMPATE": 1, "VISITANTE": 0})
        html = self.html(self.client.get(f"/admin/eventos/{self.eid}/cerrar"))
        self.assertIn("<dt>Local</dt><dd>2</dd>", html)

    def test_paso5_cancelar_lo_deja_abierto(self):
        self.assertIn("Mantener abierto", self.html(self.client.get(f"/admin/eventos/{self.eid}/cerrar")))
        self.assertEqual(S.obtener_evento(self.con, self.eid)["estado"], "Abierto")
