"""HU001 · Iniciar sesión, cerrar sesión y control de permisos por rol."""
from functools import wraps

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("auth", __name__)


@bp.before_app_request
def cargar_usuario():
    uid = session.get("uid")
    g.user = get_db().execute("SELECT * FROM usuarios WHERE id = ? AND activo = 1", (uid,)).fetchone() if uid else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def role_required(rol):
    """El permiso se valida en el servidor; no depende de ocultar botones (HU001 paso 6)."""
    def deco(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user["rol"] != rol:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return deco


@bp.route("/ingresar", methods=["GET", "POST"])
def login():
    errors, usuario = {}, ""
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip().lower()
        clave = request.form.get("clave", "")
        if not usuario:
            errors["usuario"] = "El campo usuario es obligatorio."
        if not clave:
            errors["clave"] = "El campo contraseña es obligatorio."
        if not errors:
            u = get_db().execute("SELECT * FROM usuarios WHERE usuario = ? AND activo = 1", (usuario,)).fetchone()
            if u is None or not check_password_hash(u["clave_hash"], clave):
                # Mensaje genérico: no revela si falló el usuario o la contraseña (HU001 paso 4)
                errors["_"] = "Usuario o contraseña incorrectos"
            else:
                session.clear()
                session["uid"], session["rol"] = u["id"], u["rol"]
                return redirect(url_for("admin.torneos") if u["rol"] == "admin" else url_for("participante.torneos"))
    return render_template("login.html", errors=errors, usuario=usuario), (400 if errors else 200)


@bp.route("/salir", methods=["POST", "GET"])
def logout():
    session.clear()
    flash("Sesión cerrada correctamente. Para continuar debes iniciar sesión de nuevo.", "ok")
    return redirect(url_for("auth.login"))


@bp.app_errorhandler(403)
def prohibido(_e):
    return render_template("error.html", titulo="Acceso no autorizado",
                           mensaje="No tienes permiso para realizar esta operación."), 403


@bp.app_errorhandler(404)
def no_encontrado(_e):
    return render_template("error.html", titulo="No encontrado", mensaje="El recurso solicitado no existe."), 404
