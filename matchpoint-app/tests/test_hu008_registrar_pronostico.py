"""HU008 · Registrar pronóstico (atomicidad e idempotencia)."""
from unittest import mock

from matchpoint import services as S
from tests.base import MatchPointTest


class HU008(MatchPointTest):
    def setUp(self):
        super().setUp()
        self.uid = self.participante()
        self.tid = self.torneo()
        self.eid = self.evento(self.tid, costo=100)
        self.login("laura.gomez", "demo123")

    def test_paso1_opciones_costo_y_saldo(self):
        html = self.html(self.client.get(f"/eventos/{self.eid}"))
        for t in ("Local", "Empate", "Visitante", "COSTO", "TU SALDO", "1.000"):
            self.assertIn(t, html)

    def test_paso2_valida_abierto_unico_y_saldo(self):
        self.con.execute("UPDATE usuarios SET saldo = 60 WHERE id = ?", (self.uid,))
        html = self.html(self.client.post(f"/eventos/{self.eid}", data={"opcion": "LOCAL"}))
        self.assertIn("Saldo insuficiente", html)

    def test_paso3_resumen_para_confirmar(self):
        html = self.html(self.client.post(f"/eventos/{self.eid}", data={"opcion": "LOCAL"}))
        self.assertIn("Confirmar pronóstico", html)
        self.assertIn("Saldo después", html)
        self.assertIn("900 créditos", html)
        self.assertEqual(self.count("SELECT count(*) FROM pronosticos"), 0)  # aún no se registra

    def test_paso4_registro_y_descuento_juntos(self):
        self.client.post(f"/eventos/{self.eid}/confirmar", data={"opcion": "LOCAL", "solicitud_id": "req-1"})
        self.assertEqual(self.count("SELECT count(*) FROM pronosticos"), 1)
        self.assertEqual(self.saldo(self.uid), 900)
        self.assertEqual(self.count("SELECT count(*) FROM movimientos WHERE tipo='PRONOSTICO'"), 1)

    def test_paso4_si_una_parte_falla_ninguna_se_aplica(self):
        # Se fuerza un fallo al escribir el movimiento: el pronóstico y el descuento deben deshacerse.
        con = self.con
        real = con.execute

        class Fallo:
            def __init__(self, c): self.c = c
            def execute(self, sql, *a):
                if sql.startswith("INSERT INTO movimientos"):
                    raise RuntimeError("fallo simulado")
                return self.c.execute(sql, *a)
        with self.assertRaises(RuntimeError):
            S.registrar_pronostico(Fallo(con), self.uid, self.eid, "LOCAL", "req-x")
        self.assertEqual(self.count("SELECT count(*) FROM pronosticos"), 0)
        self.assertEqual(self.saldo(self.uid), 1000)

    def test_paso5_solicitud_repetida_no_cobra_dos_veces(self):
        for _ in range(3):
            self.client.post(f"/eventos/{self.eid}/confirmar", data={"opcion": "LOCAL", "solicitud_id": "req-1"})
        self.assertEqual(self.count("SELECT count(*) FROM pronosticos"), 1)
        self.assertEqual(self.saldo(self.uid), 900)
        # Una segunda solicitud distinta para el mismo evento también se rechaza
        r = self.client.post(f"/eventos/{self.eid}/confirmar", data={"opcion": "EMPATE", "solicitud_id": "req-2"}, follow_redirects=True)
        self.assertIn("Ya registraste un pronóstico para este evento.", self.html(r))
        self.assertEqual(self.saldo(self.uid), 900)

    def test_paso6_plazo_vencido_o_saldo_insuficiente(self):
        self.con.execute("UPDATE eventos SET cierre = '2000-01-01T00:00', inicio = '2000-01-01T01:00' WHERE id = ?", (self.eid,))
        r = self.client.post(f"/eventos/{self.eid}/confirmar", data={"opcion": "LOCAL", "solicitud_id": "req-3"}, follow_redirects=True)
        self.assertIn("El plazo para pronosticar venció", self.html(r))
        self.assertEqual(self.saldo(self.uid), 1000)

    def test_paso7_cancelar_no_registra(self):
        html = self.html(self.client.post(f"/eventos/{self.eid}", data={"opcion": "LOCAL"}))
        self.assertIn(f'href="/eventos/{self.eid}">Cancelar', html)
        self.assertEqual(self.count("SELECT count(*) FROM pronosticos"), 0)
        self.assertEqual(self.saldo(self.uid), 1000)
