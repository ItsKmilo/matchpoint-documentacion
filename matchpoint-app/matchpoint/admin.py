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


# ==================================================================== SPRINT 2
def _ev_or_404(con, eid):
    ev = S.obtener_evento(con, eid)
    if ev is None:
        abort(404)
    return ev


@bp.route("/eventos/<int:eid>/cerrar", methods=["GET", "POST"])
@role_required("admin")
def cerrar_evento(eid):  # HU013
    con = get_db()
    ev = _ev_or_404(con, eid)
    if request.method == "POST":
        try:
            S.cerrar_evento(con, eid)
            flash("Evento cerrado: no se aceptan nuevos pronósticos ni anulaciones.", "ok")
        except S.ValidationError as e:
            flash(str(e), "error")
        return redirect(url_for("admin.torneo", tid=ev["tid"]))
    return render_template("admin/evento_cerrar.html", ev=ev, dist=S.distribucion(con, eid))


@bp.route("/eventos/<int:eid>/resultado", methods=["GET", "POST"])
@role_required("admin")
def resultado(eid):  # HU014
    con = get_db()
    ev = _ev_or_404(con, eid)
    form, errors, confirmar = {"goles_local": "", "goles_visitante": ""}, {}, False
    estado = S.estado_evento(ev)
    if estado == "Abierto":
        errors["_"] = "El evento sigue abierto: primero debe cerrarse la recepción de pronósticos."
    elif ev["estado"] == "Finalizado":
        errors["_"] = "El resultado ya fue publicado y no se puede sobrescribir. Usa «Corregir resultado»."
    elif request.method == "POST":
        form = {k: request.form.get(k, "") for k in ("goles_local", "goles_visitante")}
        if request.form.get("confirmado") == "1":
            try:
                S.publicar_resultado(con, eid, form["goles_local"], form["goles_visitante"])
                flash("Resultado oficial publicado. El evento quedó Finalizado.", "ok")
                return redirect(url_for("admin.torneo", tid=ev["tid"]))
            except S.ValidationError as e:
                errors = e.errors
        else:
            try:
                gl, gv = int(form["goles_local"]), int(form["goles_visitante"])
                if gl < 0 or gv < 0:
                    raise ValueError
                confirmar, form["ganador"] = True, S.OPCIONES[S._ganador(gl, gv)]
            except ValueError:
                errors["goles"] = "Ingresa un marcador válido (números enteros desde 0)."
    return render_template("admin/evento_resultado.html", ev=ev, form=form, errors=errors, confirmar=confirmar,
                           n=sum(S.distribucion(con, eid).values()))


@bp.route("/eventos/<int:eid>/liquidar", methods=["GET", "POST"])
@role_required("admin")
def liquidar(eid):  # HU015
    con = get_db()
    ev = _ev_or_404(con, eid)
    if request.method == "POST":
        try:
            n = S.liquidar_evento(con, eid)
            flash(f"Evento liquidado: se acreditaron {n} premio{'s' if n != 1 else ''}.", "ok")
        except S.ValidationError as e:
            flash(str(e), "warn")
        except Exception:
            flash("Error durante la liquidación: no se aplicó ningún abono.", "error")
        return redirect(url_for("admin.liquidar", eid=eid))
    return render_template("admin/evento_liquidar.html", ev=ev, r=S.resumen_liquidacion(con, eid))


@bp.route("/eventos/<int:eid>/corregir", methods=["GET", "POST"])
@role_required("admin")
def corregir(eid):  # HU016
    con = get_db()
    ev = _ev_or_404(con, eid)
    form, errors, imp = {"goles_local": "", "goles_visitante": "", "motivo": ""}, {}, None
    if ev["estado"] != "Finalizado":
        errors["_"] = "Solo se puede corregir el resultado de un evento finalizado."
    elif request.method == "POST":
        form = {k: request.form.get(k, "") for k in ("goles_local", "goles_visitante", "motivo")}
        aplicar = request.form.get("confirmado") == "1"
        try:
            imp = S.corregir_resultado(con, eid, g.user["id"], form["goles_local"], form["goles_visitante"], form["motivo"], aplicar=aplicar)
            if aplicar:
                flash("Resultado corregido. Se registraron las reversiones y los nuevos premios.", "ok")
                return redirect(url_for("admin.corregir", eid=eid))
        except S.ValidationError as e:
            errors, imp = e.errors, None
    historial = con.execute("SELECT c.*, u.nombre AS autor FROM correcciones_resultado c JOIN usuarios u ON u.id = c.usuario_id WHERE evento_id = ? ORDER BY c.id DESC", (eid,)).fetchall()
    return render_template("admin/evento_corregir.html", ev=ev, form=form, errors=errors, imp=imp, historial=historial)


@bp.route("/participantes/<int:uid>/ajustar", methods=["GET", "POST"])
@role_required("admin")
def ajustar(uid):  # HU017
    con = get_db()
    p = con.execute("SELECT * FROM usuarios WHERE id = ? AND rol = 'participante'", (uid,)).fetchone()
    if p is None:
        abort(404)
    form, errors, preview = {"tipo": "ABONO", "cantidad": "", "motivo": ""}, {}, None
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in ("tipo", "cantidad", "motivo")}
        aplicar = request.form.get("confirmado") == "1"
        try:
            antes, despues = S.ajustar_creditos(con, g.user["id"], uid, form["tipo"], form["cantidad"], form["motivo"], aplicar=aplicar)
            if aplicar:
                flash(f"Ajuste registrado: saldo {antes} → {despues}.", "ok")
                return redirect(url_for("admin.participante", uid=uid))
            preview = (antes, despues)
        except S.ValidationError as e:
            errors = e.errors
    return render_template("admin/ajustar.html", p=p, form=form, errors=errors, preview=preview)


@bp.route("/control/transacciones")
@role_required("admin")
def transacciones():  # HU018
    con = get_db()
    f = {k: request.args.get(k, "") for k in ("usuario", "tipo", "evento", "desde", "hasta")}
    rows = S.transacciones(con, f["usuario"] or None, f["tipo"] or None, f["evento"] or None, f["desde"] or None, f["hasta"] or None)
    sel = request.args.get("id", type=int)
    det = next((r for r in rows if r["id"] == sel), None)
    return render_template("admin/transacciones.html", rows=rows, f=f, det=det, tipos=S.TIPOS_MOV,
                           usuarios=con.execute("SELECT id, usuario FROM usuarios WHERE rol='participante' ORDER BY usuario").fetchall(),
                           eventos=con.execute("SELECT id, local, visitante FROM eventos ORDER BY inicio").fetchall())


@bp.route("/control/conciliacion")
@role_required("admin")
def conciliacion():  # HU019
    rows = S.conciliar(get_db())
    if request.args.get("formato") == "csv":
        import csv, io
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["Participante", "Usuario", "Saldo registrado", "Saldo calculado", "Diferencia", "Estado"])
        for r in rows:
            w.writerow([r["nombre"], r["usuario"], r["saldo"], r["calculado"], r["diferencia"], r["estado"]])
        return out.getvalue(), 200, {"Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=conciliacion.csv"}
    return render_template("admin/conciliacion.html", rows=rows, ejecutada=request.args.get("ejecutar") == "1")


@bp.route("/torneos/<int:tid>/reporte")
@role_required("admin")
def reporte(tid):  # HU020
    con = get_db()
    if S.obtener_torneo(con, tid) is None:
        abort(404)
    desde, hasta = request.args.get("desde", ""), request.args.get("hasta", "")
    r = S.reporte_torneo(con, tid, desde or None, hasta or None)
    if request.args.get("formato") == "csv":
        import csv, io
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["Evento", "Inicio", "Pronósticos", "Aciertos", "Créditos usados", "Premios entregados"])
        for e in r["eventos"]:
            w.writerow([f"{e['local']} vs {e['visitante']}", e["inicio"], e["pronosticos"], e["aciertos"], e["usados"], e["premios"]])
        return out.getvalue(), 200, {"Content-Type": "text/csv; charset=utf-8", "Content-Disposition": f"attachment; filename=reporte_torneo_{tid}.csv"}
    return render_template("admin/reporte.html", r=r, desde=desde, hasta=hasta)
