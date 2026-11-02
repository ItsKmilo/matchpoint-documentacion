"""HU001 · Iniciar sesión — una prueba por paso del criterio de aceptación."""
from tests.base import MatchPointTest


class HU001(MatchPointTest):
    def test_paso1_sin_sesion_muestra_login(self):
        r = self.client.get("/admin/torneos")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/ingresar", r.headers["Location"])
        html = self.html(self.client.get("/ingresar"))
        self.assertIn('name="usuario"', html)
        self.assertIn('name="clave"', html)

    def test_paso2_campos_obligatorios(self):
        html = self.html(self.client.post("/ingresar", data={"usuario": "", "clave": ""}))
        self.assertIn("El campo usuario es obligatorio.", html)
        self.assertIn("El campo contraseña es obligatorio.", html)

    def test_paso3_redirige_segun_rol(self):
        r = self.login()
        self.assertIn("/admin/torneos", r.headers["Location"])
        self.logout()
        self.participante()
        r = self.login("laura.gomez", "demo123")
        self.assertTrue(r.headers["Location"].endswith("/torneos"))

    def test_paso4_mensaje_generico(self):
        self.participante()
        a = self.html(self.login("laura.gomez", "clave-mala"))
        b = self.html(self.login("no.existe", "demo123"))
        self.assertIn("Usuario o contraseña incorrectos", a)
        self.assertIn("Usuario o contraseña incorrectos", b)

    def test_paso5_cerrar_sesion_invalida(self):
        self.login()
        self.assertEqual(self.client.get("/admin/torneos").status_code, 200)
        self.assertEqual(self.client.get("/admin/torneos").headers["Cache-Control"], "no-store")
        self.logout()
        self.assertEqual(self.client.get("/admin/torneos").status_code, 302)

    def test_paso6_participante_no_usa_funciones_admin(self):
        self.participante()
        self.login("laura.gomez", "demo123")
        self.assertEqual(self.client.get("/admin/torneos").status_code, 403)
        r = self.client.post("/admin/torneos/nuevo", data={"nombre": "X", "deporte": "Fútbol", "fecha_inicio": "2026-11-10", "fecha_fin": "2026-11-20"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.count("SELECT count(*) FROM torneos"), 0)
