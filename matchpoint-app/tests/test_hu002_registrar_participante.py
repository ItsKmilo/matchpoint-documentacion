"""HU002 · Registrar participante."""
from unittest import mock

from tests.base import MatchPointTest

DATOS = {"nombre": "Mateo Hernández", "correo": "mateo@umb.edu.co", "usuario": "mateo.h", "clave": "demo123"}


class HU002(MatchPointTest):
    def setUp(self):
        super().setUp()
        self.login()

    def test_paso1_muestra_formulario(self):
        html = self.html(self.client.get("/admin/participantes/nuevo"))
        for campo in ("nombre", "correo", "usuario", "clave"):
            self.assertIn(f'name="{campo}"', html)

    def test_paso2_valida_obligatorios_y_formato(self):
        r = self.client.post("/admin/participantes/nuevo", data={"nombre": "", "correo": "no-es-correo", "usuario": "", "clave": "x"})
        html = self.html(r)
        self.assertEqual(r.status_code, 400)
        self.assertIn("El nombre completo es obligatorio.", html)
        self.assertIn("El correo no tiene un formato válido.", html)
        self.assertIn("El usuario es obligatorio.", html)

    def test_paso3_no_permite_duplicados(self):
        self.participante("laura.gomez")
        html = self.html(self.client.post("/admin/participantes/nuevo", data={**DATOS, "correo": "laura.gomez@umb.edu.co"}))
        self.assertIn("Ya existe un participante registrado con este correo.", html)
        html = self.html(self.client.post("/admin/participantes/nuevo", data={**DATOS, "usuario": "laura.gomez"}))
        self.assertIn("Ya existe un participante registrado con este usuario.", html)
        self.assertEqual(self.count("SELECT count(*) FROM usuarios WHERE rol='participante'"), 1)

    def test_paso4_aparece_activo_con_saldo_inicial(self):
        r = self.client.post("/admin/participantes/nuevo", data=DATOS, follow_redirects=True)
        self.assertIn("Participante registrado con 1000 créditos iniciales.", self.html(r))
        lista = self.html(self.client.get("/admin/participantes"))
        self.assertIn("Mateo Hernández", lista)
        self.assertIn("Activo", lista)
        self.assertIn("1.000", lista)

    def test_paso5_cancelar_no_crea_registro(self):
        html = self.html(self.client.get("/admin/participantes/nuevo"))
        self.assertIn('href="/admin/participantes">Cancelar', html)
        self.assertEqual(self.count("SELECT count(*) FROM usuarios WHERE rol='participante'"), 0)

    def test_paso6_error_conserva_datos(self):
        with mock.patch("matchpoint.services.registrar_participante", side_effect=RuntimeError("bd caída")):
            html = self.html(self.client.post("/admin/participantes/nuevo", data=DATOS))
        self.assertIn("No se pudo guardar. Tus datos se conservaron", html)
        self.assertIn('value="Mateo Hernández"', html)
        self.assertIn('value="mateo@umb.edu.co"', html)
