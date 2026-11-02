"""Reglas de negocio de MatchPoint (Sprint 1).

Las vistas solo leen formularios y muestran resultados; toda validación y toda
operación con créditos vive aquí para poder probarla directamente.
"""
import re
import sqlite3
from datetime import date, datetime

from werkzeug.security import generate_password_hash

from .db import transaction

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USER_RE = re.compile(r"^[a-z0-9._-]{3,30}$")
OPCIONES = {"LOCAL": "Local", "EMPATE": "Empate", "VISITANTE": "Visitante"}
DEPORTES = ["Fútbol", "Baloncesto", "Voleibol", "Ajedrez", "Tenis", "Otro"]


class ValidationError(Exception):
    """Error de negocio con mensajes por campo, para mostrarlos en el formulario."""

    def __init__(self, errors, message=None):
        self.errors = errors if isinstance(errors, dict) else {"_": errors}
        super().__init__(message or "; ".join(self.errors.values()))


def now_str():
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


# ------------------------------------------------------------------ HU002 + HU009
def saldo_inicial(con):
    row = con.execute("SELECT valor FROM configuracion WHERE clave = 'saldo_inicial'").fetchone()
    return int(row["valor"]) if row else 1000


def validar_participante(con, nombre, correo, usuario, clave):
    errors = {}
    nombre, correo, usuario = nombre.strip(), correo.strip().lower(), usuario.strip().lower()
    if not nombre:
        errors["nombre"] = "El nombre completo es obligatorio."
    if not correo:
        errors["correo"] = "El correo es obligatorio."
    elif not EMAIL_RE.match(correo):
        errors["correo"] = "El correo no tiene un formato válido."
    elif con.execute("SELECT 1 FROM usuarios WHERE correo = ?", (correo,)).fetchone():
        errors["correo"] = "Ya existe un participante registrado con este correo."
    if not usuario:
        errors["usuario"] = "El usuario es obligatorio."
    elif not USER_RE.match(usuario):
        errors["usuario"] = "Usa de 3 a 30 caracteres: letras minúsculas, números, punto, guion o guion bajo."
    elif con.execute("SELECT 1 FROM usuarios WHERE usuario = ?", (usuario,)).fetchone():
        errors["usuario"] = "Ya existe un participante registrado con este usuario."
    if len(clave) < 6:
        errors["clave"] = "La contraseña inicial debe tener al menos 6 caracteres."
    if errors:
        raise ValidationError(errors)
    return nombre, correo, usuario


def asignar_creditos_iniciales(con, usuario_id):
    """HU009: crea el movimiento de asignación inicial. Debe llamarse dentro de una transacción."""
    ya = con.execute("SELECT 1 FROM movimientos WHERE usuario_id = ? AND tipo = 'ASIGNACION_INICIAL'", (usuario_id,)).fetchone()
    if ya:
        raise ValidationError("La asignación inicial ya fue aplicada a este participante.")
    monto = saldo_inicial(con)
    con.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (monto, usuario_id))
    saldo = con.execute("SELECT saldo FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()["saldo"]
    con.execute(
        "INSERT INTO movimientos (usuario_id, tipo, valor, saldo_resultante, detalle, origen) VALUES (?, 'ASIGNACION_INICIAL', ?, ?, ?, ?)",
        (usuario_id, monto, saldo, "Registro de participante", f"U-{usuario_id:04d}"),
    )
    return monto


def registrar_participante(con, nombre, correo, usuario, clave, fallar_asignacion=False):
    """HU002 + HU009: crea el participante y su saldo inicial en una sola transacción."""
    nombre, correo, usuario = validar_participante(con, nombre, correo, usuario, clave)
    with transaction(con):
        cur = con.execute(
            "INSERT INTO usuarios (usuario, correo, nombre, clave_hash, rol) VALUES (?, ?, ?, ?, 'participante')",
            (usuario, correo, nombre, generate_password_hash(clave)),
        )
        uid = cur.lastrowid
        if fallar_asignacion:  # usado en pruebas para simular un error a mitad de la operación
            raise RuntimeError("Fallo simulado en la asignación de créditos")
        asignar_creditos_iniciales(con, uid)
    return uid


def reasignar_creditos_iniciales(con, usuario_id):
    """HU009 paso 3: un segundo intento se rechaza y no suma créditos."""
    with transaction(con):
        return asignar_creditos_iniciales(con, usuario_id)


# ------------------------------------------------------------------ HU003 / HU004 / HU005
def _parse_date(value, campo, errors):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        errors[campo] = "Ingresa una fecha válida."
        return None


def validar_torneo(con, nombre, deporte, inicio, fin, excluir_id=None):
    errors = {}
    nombre = (nombre or "").strip()
    if not nombre:
        errors["nombre"] = "El nombre del torneo es obligatorio."
    if not deporte:
        errors["deporte"] = "Selecciona un deporte."
    d1 = d2 = None
    if inicio:
        d1 = _parse_date(inicio, "fecha_inicio", errors)
    else:
        errors["fecha_inicio"] = "La fecha de inicio es obligatoria."
    if fin:
        d2 = _parse_date(fin, "fecha_fin", errors)
    else:
        errors["fecha_fin"] = "La fecha de fin es obligatoria."
    if d1 and d2 and d2 < d1:
        errors["fecha_fin"] = "La fecha de fin no puede ser anterior a la de inicio."
    if not errors:
        dup = con.execute(
            "SELECT 1 FROM torneos WHERE lower(nombre) = lower(?) AND fecha_inicio = ? AND fecha_fin = ? AND id IS NOT ?",
            (nombre, inicio, fin, excluir_id),
        ).fetchone()
        if dup:
            errors["_"] = f"Ya existe «{nombre}» en esas fechas."
    if errors:
        raise ValidationError(errors)
    return nombre


def crear_torneo(con, nombre, deporte, inicio, fin, descripcion=""):
    nombre = validar_torneo(con, nombre, deporte, inicio, fin)
    with transaction(con):
        cur = con.execute(
            "INSERT INTO torneos (nombre, deporte, fecha_inicio, fecha_fin, descripcion) VALUES (?, ?, ?, ?, ?)",
            (nombre, deporte, inicio, fin, (descripcion or "").strip()),
        )
    return cur.lastrowid


def obtener_torneo(con, torneo_id):
    return con.execute("SELECT * FROM torneos WHERE id = ?", (torneo_id,)).fetchone()


def editar_torneo(con, torneo_id, usuario_id, nombre, inicio, fin, descripcion=""):
    t = obtener_torneo(con, torneo_id)
    if t is None:
        raise ValidationError("El torneo no existe.")
    if t["estado"] == "Finalizado":
        raise ValidationError("Un torneo «Finalizado» no se puede editar.")
    nombre = validar_torneo(con, nombre, t["deporte"], inicio, fin, excluir_id=torneo_id)
    rango = con.execute("SELECT min(substr(inicio, 1, 10)) AS a, max(substr(inicio, 1, 10)) AS b FROM eventos WHERE torneo_id = ?", (torneo_id,)).fetchone()
    if rango["a"] and (inicio > rango["a"] or fin < rango["b"]):
        raise ValidationError({"fecha_inicio": f"Las fechas deben cubrir todos los eventos programados ({rango['a']} a {rango['b']})."})
    cambios = []
    for campo, nuevo, etiqueta in [("nombre", nombre, "Nombre"), ("fecha_inicio", inicio, "Fecha de inicio"),
                                   ("fecha_fin", fin, "Fecha de fin"), ("descripcion", (descripcion or "").strip(), "Descripción")]:
        if t[campo] != nuevo:
            cambios.append(f"{etiqueta}: {t[campo] or '—'} → {nuevo or '—'}" if campo != "descripcion" else "Cambió la descripción")
    with transaction(con):
        con.execute("UPDATE torneos SET nombre = ?, fecha_inicio = ?, fecha_fin = ?, descripcion = ? WHERE id = ?",
                    (nombre, inicio, fin, (descripcion or "").strip(), torneo_id))
        for c in cambios:
            con.execute("INSERT INTO cambios_torneo (torneo_id, usuario_id, descripcion) VALUES (?, ?, ?)", (torneo_id, usuario_id, c))
    return cambios


def contar_eventos(con, torneo_id):
    return con.execute("SELECT count(*) AS n FROM eventos WHERE torneo_id = ?", (torneo_id,)).fetchone()["n"]


def eliminar_torneo(con, torneo_id):
    t = obtener_torneo(con, torneo_id)
    if t is None:
        raise ValidationError("El torneo no existe.")
    n = contar_eventos(con, torneo_id)
    if n:
        raise ValidationError(f"No es posible eliminar «{t['nombre']}» porque el torneo está vinculado a {n} evento{'s' if n != 1 else ''}.")
    with transaction(con):
        con.execute("DELETE FROM torneos WHERE id = ?", (torneo_id,))
    return t["nombre"]


# ------------------------------------------------------------------ HU006
def crear_evento(con, torneo_id, local, visitante, inicio, cierre, costo, premio):
    t = obtener_torneo(con, torneo_id)
    if t is None:
        raise ValidationError("El torneo no existe.")
    errors = {}
    local, visitante = (local or "").strip(), (visitante or "").strip()
    if not local:
        errors["local"] = "El contendiente local es obligatorio."
    if not visitante:
        errors["visitante"] = "El contendiente visitante es obligatorio."
    if local and visitante and local.lower() == visitante.lower():
        errors["visitante"] = "El mismo contendiente no puede estar en los dos lados."
    di = dc = None
    try:
        di = datetime.fromisoformat(inicio)
    except (TypeError, ValueError):
        errors["inicio"] = "Ingresa la fecha y hora del encuentro."
    try:
        dc = datetime.fromisoformat(cierre)
    except (TypeError, ValueError):
        errors["cierre"] = "Ingresa la fecha límite para pronosticar."
    if di and dc:
        if dc >= di:
            errors["cierre"] = "Debe ser anterior al inicio del encuentro."
        rango = f"{t['fecha_inicio']} a {t['fecha_fin']}"
        if not (t["fecha_inicio"] <= di.date().isoformat() <= t["fecha_fin"]):
            errors["inicio"] = f"Debe estar dentro del rango del torneo ({rango})."
        if not (t["fecha_inicio"] <= dc.date().isoformat() <= t["fecha_fin"]):
            errors.setdefault("cierre", f"Debe estar dentro del rango del torneo ({rango}).")
    for campo, val, nombre in [("costo", costo, "El costo"), ("premio", premio, "El premio")]:
        try:
            if int(val) <= 0:
                raise ValueError
        except (TypeError, ValueError):
            errors[campo] = f"{nombre} debe ser un número entero mayor que cero."
    if errors:
        raise ValidationError(errors)
    with transaction(con):
        cur = con.execute(
            "INSERT INTO eventos (torneo_id, local, visitante, inicio, cierre, costo, premio) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (torneo_id, local, visitante, di.strftime("%Y-%m-%dT%H:%M"), dc.strftime("%Y-%m-%dT%H:%M"), int(costo), int(premio)),
        )
    return cur.lastrowid


def estado_evento(ev, ahora=None):
    """El estado se muestra 'Cerrado' en cuanto pasa la fecha límite, aunque nadie lo haya cerrado a mano."""
    ahora = ahora or now_str()
    if ev["estado"] == "Abierto" and ev["cierre"] <= ahora:
        return "Cerrado"
    return ev["estado"]


# ------------------------------------------------------------------ HU007
def torneos_activos(con):
    return con.execute(
        "SELECT t.*, (SELECT count(*) FROM eventos e WHERE e.torneo_id = t.id) AS n_eventos FROM torneos t "
        "WHERE t.estado IN ('Programado', 'En curso') ORDER BY t.fecha_inicio, t.nombre"
    ).fetchall()


def eventos_de_torneo(con, torneo_id, filtro=None):
    evs = con.execute("SELECT * FROM eventos WHERE torneo_id = ? ORDER BY inicio", (torneo_id,)).fetchall()
    out = []
    for e in evs:
        d = dict(e)
        d["estado_actual"] = estado_evento(e)
        if filtro and d["estado_actual"] != filtro:
            continue
        out.append(d)
    return out


# ------------------------------------------------------------------ HU008
class ForecastError(ValidationError):
    pass


def registrar_pronostico(con, usuario_id, evento_id, opcion, solicitud_id, ahora=None):
    """HU008: valida y registra el pronóstico con su descuento en UNA transacción.

    Devuelve (pronostico_id, nuevo) — nuevo=False cuando la solicitud ya se había procesado
    (doble clic o reintento): no se registra otro pronóstico ni otro descuento.
    """
    if opcion not in OPCIONES:
        raise ForecastError("Selecciona una opción válida.")
    if not solicitud_id:
        raise ForecastError("Solicitud inválida. Vuelve a intentarlo.")
    with transaction(con):
        previo = con.execute("SELECT id, usuario_id FROM pronosticos WHERE solicitud_id = ?", (solicitud_id,)).fetchone()
        if previo:
            if previo["usuario_id"] != usuario_id:
                raise ForecastError("Solicitud inválida.")
            return previo["id"], False
        ev = con.execute("SELECT e.*, t.nombre AS torneo FROM eventos e JOIN torneos t ON t.id = e.torneo_id WHERE e.id = ?", (evento_id,)).fetchone()
        if ev is None:
            raise ForecastError("El evento no existe.")
        if estado_evento(ev, ahora) != "Abierto":
            raise ForecastError("El plazo para pronosticar venció. No se realizó ningún descuento.")
        if con.execute("SELECT 1 FROM pronosticos WHERE evento_id = ? AND usuario_id = ?", (evento_id, usuario_id)).fetchone():
            raise ForecastError("Ya registraste un pronóstico para este evento.")
        saldo = con.execute("SELECT saldo FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()["saldo"]
        if saldo < ev["costo"]:
            raise ForecastError(f"Saldo insuficiente: tienes {saldo} créditos y el evento cuesta {ev['costo']}. No se descontó nada.")
        cur = con.execute(
            "INSERT INTO pronosticos (evento_id, usuario_id, opcion, costo, solicitud_id) VALUES (?, ?, ?, ?, ?)",
            (evento_id, usuario_id, opcion, ev["costo"], solicitud_id),
        )
        pid = cur.lastrowid
        # El WHERE saldo >= costo protege también ante dos solicitudes simultáneas.
        upd = con.execute("UPDATE usuarios SET saldo = saldo - ? WHERE id = ? AND saldo >= ?", (ev["costo"], usuario_id, ev["costo"]))
        if upd.rowcount != 1:
            raise ForecastError("Saldo insuficiente. No se descontó nada.")
        nuevo_saldo = con.execute("SELECT saldo FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()["saldo"]
        con.execute(
            "INSERT INTO movimientos (usuario_id, tipo, valor, saldo_resultante, detalle, origen) VALUES (?, 'PRONOSTICO', ?, ?, ?, ?)",
            (usuario_id, -ev["costo"], nuevo_saldo, f"{ev['local']} vs {ev['visitante']} · {OPCIONES[opcion]}", f"P-{pid:04d}"),
        )
    return pid, True


# ------------------------------------------------------------------ HU010
def movimientos_de(con, usuario_id):
    return con.execute("SELECT * FROM movimientos WHERE usuario_id = ? ORDER BY id DESC", (usuario_id,)).fetchall()


def verificar_saldo(con, usuario_id):
    """HU010 paso 4: el saldo debe coincidir con la suma de los movimientos."""
    saldo = con.execute("SELECT saldo FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()["saldo"]
    suma = con.execute("SELECT coalesce(sum(valor), 0) AS s FROM movimientos WHERE usuario_id = ?", (usuario_id,)).fetchone()["s"]
    return saldo, suma, saldo == suma
