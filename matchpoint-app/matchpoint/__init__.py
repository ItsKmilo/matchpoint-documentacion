"""MatchPoint · Plataforma de torneos, pronósticos y créditos virtuales (Sprint 1)."""
import os
from pathlib import Path

from flask import Flask, redirect, session, url_for

from . import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("MATCHPOINT_SECRET", "cambia-esta-clave-en-produccion"),
        DATABASE=str(Path(app.instance_path) / "matchpoint.sqlite"),
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    if not Path(app.config["DATABASE"]).exists() or app.config.get("TESTING"):
        db.init_db(app.config["DATABASE"])

    from .auth import bp as auth_bp
    from .admin import bp as admin_bp
    from .participante import bp as part_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(part_bp)

    @app.after_request
    def no_cache(resp):
        # HU001 paso 5: después de cerrar sesión, «Atrás» no debe mostrar pantallas privadas guardadas.
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.route("/")
    def index():
        if session.get("rol") == "admin":
            return redirect(url_for("admin.torneos"))
        if session.get("rol") == "participante":
            return redirect(url_for("participante.torneos"))
        return redirect(url_for("auth.login"))

    @app.template_filter("fecha")
    def fecha(value):
        if not value:
            return ""
        v = str(value).replace("T", " ")
        d = v[:10].split("-")
        return f"{d[2]}/{d[1]}/{d[0]}{(' · ' + v[11:16]) if len(v) > 10 else ''}"

    @app.template_filter("tipo_mov")
    def tipo_mov(value):
        return {"ASIGNACION_INICIAL": "Asignación inicial", "PRONOSTICO": "Pronóstico", "PREMIO": "Premio",
                "REINTEGRO": "Reintegro", "AJUSTE": "Ajuste"}.get(value, value)

    @app.template_filter("creditos")
    def creditos(value):
        return f"{int(value):,}".replace(",", ".")

    return app
