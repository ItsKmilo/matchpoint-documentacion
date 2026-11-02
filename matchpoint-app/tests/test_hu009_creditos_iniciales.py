"""HU009 · Asignar créditos iniciales."""
from matchpoint import services as S
from tests.base import MatchPointTest


class HU009(MatchPointTest):
    def test_paso1_asigna_saldo_inicial(self):
        uid = self.participante()
        self.assertEqual(self.saldo(uid), 1000)

    def test_paso2_queda_movimiento_de_asignacion(self):
        uid = self.participante()
        m = self.con.execute("SELECT * FROM movimientos WHERE usuario_id = ?", (uid,)).fetchone()
        self.assertEqual((m["tipo"], m["valor"], m["saldo_resultante"]), ("ASIGNACION_INICIAL", 1000, 1000))
        self.assertTrue(m["creado_en"])

    def test_paso3_no_se_asigna_dos_veces(self):
        uid = self.participante()
        with self.assertRaises(S.ValidationError):
            S.reasignar_creditos_iniciales(self.con, uid)
        self.assertEqual(self.saldo(uid), 1000)
        self.login()
        r = self.client.post(f"/admin/participantes/{uid}/asignacion-inicial", follow_redirects=True)
        self.assertIn("La asignación inicial ya fue aplicada a este participante.", self.html(r))

    def test_paso4_admin_consulta_valor_configurado(self):
        uid = self.participante()
        self.login()
        html = self.html(self.client.get(f"/admin/participantes/{uid}"))
        self.assertIn("Saldo inicial por participante: <b>1.000</b>", html)
        self.assertIn("sin valor monetario", html)

    def test_paso5_error_revierte_todo(self):
        with self.assertRaises(RuntimeError):
            S.registrar_participante(self.con, "Ana", "ana@umb.edu.co", "ana", "demo123", fallar_asignacion=True)
        self.assertEqual(self.count("SELECT count(*) FROM usuarios WHERE usuario = 'ana'"), 0)
        self.assertEqual(self.count("SELECT count(*) FROM movimientos"), 0)
