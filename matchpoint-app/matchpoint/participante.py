"""Vistas del participante: HU007, HU008 y HU010."""
import uuid

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from . import services as S
from .auth import role_required
from .db import get_db

bp = Blueprint("participante", __name__)
FILTROS = {"abiertos": "Abierto", "cerrados": "Cerrado", "finalizados": "Finalizado"}


@bp.route("/torneos")
@role_required("participante")
def torneos():
    con = get_db()
    lista = S.torneos_activos(con)
    tid = request.args.get("torneo", type=int) or (lista[0]["id"] if lista else None)
    filtro = request.args.get("estado", "todos")
    actual = next((t for t in lista if t["id"] == tid), None)
    eventos = S.eventos_de_torneo(con, tid, FILTROS.get(filtro)) if actual else []
    return render_template("participante/torneos.html", torneos=lista, actual=actual, eventos=eventos, filtro=filtro)


def _evento(con, eid):
    ev = con.execute("SELECT e.*, t.nombre AS torneo, t.id AS tid FROM eventos e JOIN torneos t ON t.id = e.torneo_id WHERE e.id = ?", (eid,)).fetchone()
    if ev is None:
        abort(404)
    return ev


@bp.route("/eventos/<int:eid>", methods=["GET", "POST"])
@role_required("participante")
def evento(eid):
    """Paso 1: opciones, costo y saldo. Paso 2-3: valida y muestra el resumen para confirmar."""
    con = get_db()
    ev = _evento(con, eid)
    estado = S.estado_evento(ev)
    ya = con.execute("SELECT * FROM pronosticos WHERE evento_id = ? AND usuario_id = ?", (eid, g.user["id"])).fetchone()
    error, confirmar, opcion = None, False, request.form.get("opcion") or request.args.get("opcion")
    if request.method == "POST":
        if opcion not in S.OPCIONES:
            error = "Selecciona una opción."
        elif estado != "Abierto":
            error = "El plazo para pronosticar venció. No se realizó ningún descuento."
        elif ya:
            error = "Ya registraste un pronóstico para este evento."
        elif g.user["saldo"] < ev["costo"]:
            error = f"Saldo insuficiente: tienes {g.user['saldo']} créditos y el evento cuesta {ev['costo']}. No se descontó nada."
        else:
            confirmar = True
    return render_template("participante/evento.html", ev=ev, estado=estado, ya=ya, error=error, confirmar=confirmar,
                           opcion=opcion, opciones=S.OPCIONES, solicitud_id=str(uuid.uuid4())), (400 if error else 200)


@bp.route("/eventos/<int:eid>/confirmar", methods=["POST"])
@role_required("participante")
def confirmar(eid):
    """Paso 4-6: registra el pronóstico y el descuento juntos; una solicitud repetida no se cobra dos veces."""
    con = get_db()
    _evento(con, eid)
    try:
        pid, nuevo = S.registrar_pronostico(con, g.user["id"], eid, request.form.get("opcion"), request.form.get("solicitud_id"))
    except S.ValidationError as e:
        flash(str(e), "error")
        return redirect(url_for("participante.evento", eid=eid))
    if nuevo:
        flash(f"Pronóstico P-{pid:04d} registrado. Se descontaron los créditos del evento.", "ok")
    else:
        flash(f"Tu pronóstico P-{pid:04d} ya estaba registrado. No se hizo un segundo descuento.", "info")
    return redirect(url_for("participante.evento", eid=eid))


@bp.route("/mis-creditos")
@bp.route("/creditos/<int:uid>")
@role_required("participante")
def creditos(uid=None):
    if uid is not None and uid != g.user["id"]:
        abort(403)  # HU010 paso 5
    con = get_db()
    saldo, suma, ok = S.verificar_saldo(con, g.user["id"])
    return render_template("participante/creditos.html", movimientos=S.movimientos_de(con, g.user["id"]), saldo=saldo, suma=suma, ok=ok)
