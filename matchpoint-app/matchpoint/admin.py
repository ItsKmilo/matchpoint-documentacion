"""Vistas del administrador: HU002, HU003, HU004, HU005, HU006 y HU009."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from . import services as S
from .auth import role_required
from .db import get_db

bp = Blueprint("admin", __name__, url_prefix="/admin")


# ------------------------------------------------------------------ participantes (HU002, HU009)
@bp.route("/participantes")
@role_required("admin")
def participantes():
    con = get_db()
    rows = con.execute("SELECT * FROM usuarios WHERE rol = 'participante' ORDER BY nombre").fetchall()
    return render_template("admin/participantes.html", participantes=rows)


@bp.route("/participantes/nuevo", methods=["GET", "POST"])
@role_required("admin")
def nuevo_participante():
    con = get_db()
    form, errors = {}, {}
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in ("nombre", "correo", "usuario", "clave")}
        try:
            uid = S.registrar_participante(con, **form)
        except S.ValidationError as e:
            errors = e.errors
        except Exception:  # HU002 paso 6: se notifica y se conservan los datos
            errors = {"_": "No se pudo guardar. Tus datos se conservaron, intenta de nuevo."}
        else:
            flash(f"Participante registrado con {S.saldo_inicial(con)} créditos iniciales.", "ok")
            return redirect(url_for("admin.participante", uid=uid))
    return render_template("admin/participante_form.html", form=form, errors=errors,
                           saldo_inicial=S.saldo_inicial(con)), (400 if errors else 200)


@bp.route("/participantes/<int:uid>")
@role_required("admin")
def participante(uid):
    con = get_db()
    p = con.execute("SELECT * FROM usuarios WHERE id = ? AND rol = 'participante'", (uid,)).fetchone()
    if p is None:
        abort(404)
    return render_template("admin/participante.html", p=p, movimientos=S.movimientos_de(con, uid),
                           saldo_inicial=S.saldo_inicial(con))


@bp.route("/participantes/<int:uid>/asignacion-inicial", methods=["POST"])
@role_required("admin")
def asignacion_inicial(uid):
    try:
        S.reasignar_creditos_iniciales(get_db(), uid)
        flash("Asignación inicial aplicada.", "ok")
    except S.ValidationError as e:
        flash(str(e) + " No se sumaron créditos adicionales.", "warn")
    return redirect(url_for("admin.participante", uid=uid))


# ------------------------------------------------------------------ torneos (HU003, HU004, HU005)
@bp.route("/torneos")
@role_required("admin")
def torneos():
    con = get_db()
    rows = con.execute(
        "SELECT t.*, (SELECT count(*) FROM eventos e WHERE e.torneo_id = t.id) AS n_eventos FROM torneos t ORDER BY t.fecha_inicio DESC, t.nombre"
    ).fetchall()
    return render_template("admin/torneos.html", torneos=rows)


@bp.route("/torneos/nuevo", methods=["GET", "POST"])
@role_required("admin")
def nuevo_torneo():
    form, errors = {}, {}
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in ("nombre", "deporte", "fecha_inicio", "fecha_fin", "descripcion")}
        try:
            S.crear_torneo(get_db(), form["nombre"], form["deporte"], form["fecha_inicio"], form["fecha_fin"], form["descripcion"])
        except S.ValidationError as e:
            errors = e.errors
        except Exception:  # HU003 paso 6
            flash("No se pudo guardar el torneo. Volviste a la lista de torneos.", "error")
            return redirect(url_for("admin.torneos"))
        else:
            flash(f"Torneo «{form['nombre'].strip()}» creado con estado Programado.", "ok")
            return redirect(url_for("admin.torneos"))
    return render_template("admin/torneo_form.html", form=form, errors=errors, deportes=S.DEPORTES, modo="crear"), (400 if errors else 200)


@bp.route("/torneos/<int:tid>/editar", methods=["GET", "POST"])
@role_required("admin")
def editar_torneo(tid):
    con = get_db()
    t = S.obtener_torneo(con, tid)
    if t is None:
        abort(404)
    form, errors = dict(t), {}
    if t["estado"] == "Finalizado":
        errors = {"_": "Un torneo «Finalizado» no se puede editar."}
    elif request.method == "POST":
        form.update({k: request.form.get(k, "") for k in ("nombre", "fecha_inicio", "fecha_fin", "descripcion")})
        try:
            cambios = S.editar_torneo(con, tid, g.user["id"], form["nombre"], form["fecha_inicio"], form["fecha_fin"], form["descripcion"])
        except S.ValidationError as e:
            errors = e.errors
        else:
            flash("Cambios guardados." if cambios else "No había cambios para guardar.", "ok")
            return redirect(url_for("admin.torneos"))
    historial = con.execute(
        "SELECT c.*, u.nombre AS autor FROM cambios_torneo c JOIN usuarios u ON u.id = c.usuario_id WHERE torneo_id = ? ORDER BY c.id DESC", (tid,)
    ).fetchall()
    return render_template("admin/torneo_form.html", form=form, errors=errors, deportes=S.DEPORTES, modo="editar", t=t,
                           historial=historial, n_eventos=S.contar_eventos(con, tid)), (400 if errors and request.method == "POST" else 200)


@bp.route("/torneos/<int:tid>/eliminar", methods=["GET", "POST"])
@role_required("admin")
def eliminar_torneo(tid):
    con = get_db()
    t = S.obtener_torneo(con, tid)
    if t is None:
        abort(404)
    n = S.contar_eventos(con, tid)
    if n:  # HU005 paso 1 y 6: se valida antes de mostrar la confirmación
        flash(f"No es posible eliminar «{t['nombre']}» porque el torneo está vinculado a {n} evento{'s' if n != 1 else ''}. "
              "Puedes cambiar su estado desde Editar.", "error")
        return redirect(url_for("admin.torneos"))
    if request.method == "POST":
        try:
            nombre = S.eliminar_torneo(con, tid)
        except S.ValidationError as e:
            flash(str(e), "error")
        except Exception:  # HU005 paso 5
            flash("Ocurrió un error al eliminar. Se recargó la lista de torneos.", "error")
        else:
            flash(f"Torneo «{nombre}» eliminado.", "ok")
        return redirect(url_for("admin.torneos"))
    return render_template("admin/torneo_eliminar.html", t=t)


# ------------------------------------------------------------------ eventos (HU006)
@bp.route("/torneos/<int:tid>")
@role_required("admin")
def torneo(tid):
    con = get_db()
    t = S.obtener_torneo(con, tid)
    if t is None:
        abort(404)
    return render_template("admin/torneo.html", t=t, eventos=S.eventos_de_torneo(con, tid))


@bp.route("/torneos/<int:tid>/eventos/nuevo", methods=["GET", "POST"])
@role_required("admin")
def nuevo_evento(tid):
    con = get_db()
    t = S.obtener_torneo(con, tid)
    if t is None:
        abort(404)
    form, errors = {"costo": "100", "premio": "250"}, {}
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in ("local", "visitante", "inicio", "cierre", "costo", "premio")}
        try:
            S.crear_evento(con, tid, **form)
        except S.ValidationError as e:
            errors = e.errors
        else:
            flash(f"Evento {form['local']} vs {form['visitante']} programado con estado Abierto.", "ok")
            return redirect(url_for("admin.torneo", tid=tid))
    return render_template("admin/evento_form.html", t=t, form=form, errors=errors,
                           eventos=S.eventos_de_torneo(con, tid)), (400 if errors else 200)
