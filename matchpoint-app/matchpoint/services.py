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
            "INSERT INTO movimientos (usuario_id, tipo, valor, saldo_resultante, detalle, origen, evento_id) VALUES (?, 'PRONOSTICO', ?, ?, ?, ?, ?)",
            (usuario_id, -ev["costo"], nuevo_saldo, f"{ev['local']} vs {ev['visitante']} · {OPCIONES[opcion]}", f"P-{pid:04d}", evento_id),
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


# ==================================================================== SPRINT 2
def _ganador(gl, gv):
    return "LOCAL" if gl > gv else ("VISITANTE" if gv > gl else "EMPATE")


def _mov(con, usuario_id, tipo, valor, detalle, origen, evento_id=None, autor_id=None):
    """Aplica un cambio de saldo y deja su movimiento. Debe llamarse dentro de una transacción."""
    upd = con.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ? AND saldo + ? >= 0", (valor, usuario_id, valor))
    if upd.rowcount != 1:
        raise ValidationError("La operación dejaría el saldo en negativo.")
    saldo = con.execute("SELECT saldo FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()["saldo"]
    con.execute("INSERT INTO movimientos (usuario_id, tipo, valor, saldo_resultante, detalle, origen, evento_id, autor_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (usuario_id, tipo, valor, saldo, detalle, origen, evento_id, autor_id))
    return saldo


def obtener_evento(con, evento_id):
    return con.execute("SELECT e.*, t.nombre AS torneo, t.id AS tid FROM eventos e JOIN torneos t ON t.id = e.torneo_id WHERE e.id = ?", (evento_id,)).fetchone()


# ------------------------------------------------------------------ HU011
def mis_pronosticos(con, usuario_id):
    return con.execute(
        "SELECT p.*, e.local, e.visitante, e.inicio, e.cierre, e.estado AS ev_estado, e.resultado, e.goles_local, e.goles_visitante, "
        "e.publicado_en, e.premio, t.nombre AS torneo, "
        "(SELECT coalesce(sum(m.valor), 0) FROM movimientos m WHERE m.origen = 'P-' || printf('%04d', p.id) AND m.tipo = 'PREMIO') AS premio_recibido "
        "FROM pronosticos p JOIN eventos e ON e.id = p.evento_id JOIN torneos t ON t.id = e.torneo_id "
        "WHERE p.usuario_id = ? ORDER BY p.id DESC", (usuario_id,)).fetchall()


# ------------------------------------------------------------------ HU012
def anular_pronostico(con, usuario_id, pronostico_id, ahora=None):
    with transaction(con):
        p = con.execute("SELECT * FROM pronosticos WHERE id = ? AND usuario_id = ?", (pronostico_id, usuario_id)).fetchone()
        if p is None:
            raise ValidationError("El pronóstico no existe.")
        if p["estado"] == "Anulado":
            raise ValidationError("Este pronóstico ya fue anulado. No se generó otro reintegro.")
        if p["estado"] != "Pendiente":
            raise ValidationError("Solo se pueden anular pronósticos pendientes.")
        ev = obtener_evento(con, p["evento_id"])
        if estado_evento(ev, ahora) != "Abierto":
            raise ValidationError("No es posible anular el pronóstico porque el evento está cerrado.")
        con.execute("UPDATE pronosticos SET estado = 'Anulado' WHERE id = ?", (pronostico_id,))
        _mov(con, usuario_id, "REINTEGRO", p["costo"], f"Anulación · {ev['local']} vs {ev['visitante']}", f"P-{pronostico_id:04d}", ev["id"])
    return p["costo"]


# ------------------------------------------------------------------ HU013
def distribucion(con, evento_id):
    rows = con.execute("SELECT opcion, count(*) AS n FROM pronosticos WHERE evento_id = ? AND estado <> 'Anulado' GROUP BY opcion", (evento_id,)).fetchall()
    d = {k: 0 for k in OPCIONES}
    d.update({r["opcion"]: r["n"] for r in rows})
    return d


def cerrar_evento(con, evento_id):
    ev = obtener_evento(con, evento_id)
    if ev is None:
        raise ValidationError("El evento no existe.")
    if ev["estado"] != "Abierto":
        raise ValidationError("El evento ya no está abierto.")
    with transaction(con):
        con.execute("UPDATE eventos SET estado = 'Cerrado' WHERE id = ?", (evento_id,))


# ------------------------------------------------------------------ HU014
def publicar_resultado(con, evento_id, goles_local, goles_visitante):
    ev = obtener_evento(con, evento_id)
    if ev is None:
        raise ValidationError("El evento no existe.")
    if ev["estado"] == "Finalizado":
        raise ValidationError("El resultado ya fue publicado y no se puede sobrescribir. Usa «Corregir resultado».")
    if estado_evento(ev) != "Cerrado":
        raise ValidationError("El evento sigue abierto: primero debe cerrarse la recepción de pronósticos.")
    try:
        gl, gv = int(goles_local), int(goles_visitante)
        if gl < 0 or gv < 0:
            raise ValueError
    except (TypeError, ValueError):
        raise ValidationError({"goles": "Ingresa un marcador válido (números enteros desde 0)."})
    with transaction(con):
        con.execute("UPDATE eventos SET estado = 'Finalizado', goles_local = ?, goles_visitante = ?, resultado = ?, publicado_en = datetime('now','localtime') WHERE id = ?",
                    (gl, gv, _ganador(gl, gv), evento_id))
    return _ganador(gl, gv)


# ------------------------------------------------------------------ HU015
def resumen_liquidacion(con, evento_id):
    ev = obtener_evento(con, evento_id)
    ps = con.execute("SELECT p.*, u.nombre FROM pronosticos p JOIN usuarios u ON u.id = p.usuario_id WHERE evento_id = ? AND p.estado <> 'Anulado' ORDER BY p.id", (evento_id,)).fetchall()
    gan = [p for p in ps if ev["resultado"] and p["opcion"] == ev["resultado"]]
    return {"evento": ev, "total": len(ps), "acertados": len(gan), "no_acertados": len(ps) - len(gan),
            "a_acreditar": len(gan) * ev["premio"], "ganadores": gan}


def liquidar_evento(con, evento_id):
    with transaction(con):
        ev = obtener_evento(con, evento_id)
        if ev is None:
            raise ValidationError("El evento no existe.")
        if ev["liquidado_en"]:
            raise ValidationError(f"Este evento ya fue liquidado el {ev['liquidado_en']}. No se acreditarán premios duplicados.")
        if ev["estado"] != "Finalizado":
            raise ValidationError("Solo se puede liquidar un evento con resultado oficial publicado.")
        n = 0
        for p in con.execute("SELECT * FROM pronosticos WHERE evento_id = ? AND estado = 'Pendiente'", (evento_id,)).fetchall():
            if p["opcion"] == ev["resultado"]:
                con.execute("UPDATE pronosticos SET estado = 'Acertado' WHERE id = ?", (p["id"],))
                _mov(con, p["usuario_id"], "PREMIO", ev["premio"], f"Acierto · {ev['local']} vs {ev['visitante']}", f"P-{p['id']:04d}", evento_id)
                n += 1
            else:
                con.execute("UPDATE pronosticos SET estado = 'No acertado' WHERE id = ?", (p["id"],))
        con.execute("UPDATE eventos SET liquidado_en = datetime('now','localtime') WHERE id = ?", (evento_id,))
    return n


# ------------------------------------------------------------------ HU016
def _marcador(gl, gv):
    return f"{gl} – {gv} ({OPCIONES[_ganador(gl, gv)]})"


def impacto_correccion(con, evento_id, nuevo):
    ev = obtener_evento(con, evento_id)
    ps = con.execute("SELECT * FROM pronosticos WHERE evento_id = ? AND estado IN ('Acertado', 'No acertado', 'Pendiente')", (evento_id,)).fetchall()
    revertir = [p for p in ps if p["estado"] == "Acertado" and p["opcion"] != nuevo] if ev["liquidado_en"] else []
    acreditar = [p for p in ps if p["estado"] == "No acertado" and p["opcion"] == nuevo] if ev["liquidado_en"] else []
    return {"revertir": revertir, "acreditar": acreditar, "premio": ev["premio"]}


def corregir_resultado(con, evento_id, usuario_id, goles_local, goles_visitante, motivo, aplicar=True):
    ev = obtener_evento(con, evento_id)
    if ev is None or ev["estado"] != "Finalizado":
        raise ValidationError("Solo se puede corregir el resultado de un evento finalizado.")
    errors = {}
    try:
        gl, gv = int(goles_local), int(goles_visitante)
        if gl < 0 or gv < 0:
            raise ValueError
    except (TypeError, ValueError):
        errors["goles"] = "Ingresa un marcador válido."
    if not (motivo or "").strip():
        errors["motivo"] = "El motivo de la corrección es obligatorio."
    if errors:
        raise ValidationError(errors)
    if (gl, gv) == (ev["goles_local"], ev["goles_visitante"]):
        raise ValidationError({"goles": "El nuevo marcador es igual al publicado."})
    nuevo = _ganador(gl, gv)
    imp = impacto_correccion(con, evento_id, nuevo)
    if not aplicar:
        return imp
    # HU016 paso 6: si una reversión deja saldo negativo, no se aplica nada
    afectados = [r["usuario"] for r in con.execute(
        f"SELECT u.usuario FROM usuarios u WHERE u.id IN ({','.join('?' * len(imp['revertir'])) or 'NULL'}) AND u.saldo < ?",
        [p["usuario_id"] for p in imp["revertir"]] + [ev["premio"]]).fetchall()]
    if afectados:
        raise ValidationError(f"No se aplicó la corrección: quedarían con saldo negativo {', '.join(afectados)}.")
    with transaction(con):
        for p in imp["revertir"]:
            con.execute("UPDATE pronosticos SET estado = 'No acertado' WHERE id = ?", (p["id"],))
            _mov(con, p["usuario_id"], "PREMIO", -ev["premio"], f"Reversión por corrección · {ev['local']} vs {ev['visitante']}", f"P-{p['id']:04d}", evento_id)
        for p in imp["acreditar"]:
            con.execute("UPDATE pronosticos SET estado = 'Acertado' WHERE id = ?", (p["id"],))
            _mov(con, p["usuario_id"], "PREMIO", ev["premio"], f"Premio por corrección · {ev['local']} vs {ev['visitante']}", f"P-{p['id']:04d}", evento_id)
        con.execute("UPDATE eventos SET goles_local = ?, goles_visitante = ?, resultado = ? WHERE id = ?", (gl, gv, nuevo, evento_id))
        con.execute("INSERT INTO correcciones_resultado (evento_id, usuario_id, anterior, nuevo, motivo) VALUES (?, ?, ?, ?, ?)",
                    (evento_id, usuario_id, _marcador(ev["goles_local"], ev["goles_visitante"]), _marcador(gl, gv), motivo.strip()))
    return imp


# ------------------------------------------------------------------ HU017
def ajustar_creditos(con, autor_id, usuario_id, tipo, cantidad, motivo, aplicar=True):
    errors = {}
    if tipo not in ("ABONO", "CARGO"):
        errors["tipo"] = "Elige abono o cargo."
    try:
        cant = int(cantidad)
        if cant <= 0:
            raise ValueError
    except (TypeError, ValueError):
        errors["cantidad"] = "La cantidad debe ser un número entero mayor que cero."
        cant = 0
    if not (motivo or "").strip():
        errors["motivo"] = "El motivo es obligatorio."
    saldo = con.execute("SELECT saldo FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()["saldo"]
    valor = cant if tipo == "ABONO" else -cant
    if not errors and saldo + valor < 0:
        errors["cantidad"] = f"El cargo dejaría el saldo en negativo (saldo actual {saldo})."
    if errors:
        raise ValidationError(errors)
    if not aplicar:
        return saldo, saldo + valor
    with transaction(con):
        nuevo = _mov(con, usuario_id, "AJUSTE", valor, f"Ajuste: {motivo.strip()}", f"A-{autor_id:04d}", None, autor_id)
    return saldo, nuevo


# ------------------------------------------------------------------ HU018
TIPOS_MOV = ["ASIGNACION_INICIAL", "PRONOSTICO", "PREMIO", "REINTEGRO", "AJUSTE"]


def transacciones(con, usuario_id=None, tipo=None, evento_id=None, desde=None, hasta=None):
    sql = ("SELECT m.*, u.usuario, a.usuario AS autor FROM movimientos m JOIN usuarios u ON u.id = m.usuario_id "
           "LEFT JOIN usuarios a ON a.id = m.autor_id WHERE 1 = 1")
    args = []
    if usuario_id:
        sql += " AND m.usuario_id = ?"; args.append(usuario_id)
    if tipo:
        sql += " AND m.tipo = ?"; args.append(tipo)
    if evento_id:
        sql += " AND m.evento_id = ?"; args.append(evento_id)
    if desde:
        sql += " AND substr(m.creado_en, 1, 10) >= ?"; args.append(desde)
    if hasta:
        sql += " AND substr(m.creado_en, 1, 10) <= ?"; args.append(hasta)
    return con.execute(sql + " ORDER BY m.id DESC", args).fetchall()


# ------------------------------------------------------------------ HU019
def conciliar(con):
    rows = con.execute("SELECT u.id, u.nombre, u.usuario, u.saldo, coalesce(sum(m.valor), 0) AS calculado FROM usuarios u "
                       "LEFT JOIN movimientos m ON m.usuario_id = u.id WHERE u.rol = 'participante' GROUP BY u.id ORDER BY u.nombre").fetchall()
    return [{**dict(r), "diferencia": r["saldo"] - r["calculado"], "estado": "Correcto" if r["saldo"] == r["calculado"] else "Inconsistente"} for r in rows]


# ------------------------------------------------------------------ HU020
def reporte_torneo(con, torneo_id, desde=None, hasta=None):
    t = obtener_torneo(con, torneo_id)
    filtro, args = "", [torneo_id]
    if desde:
        filtro += " AND substr(e.inicio, 1, 10) >= ?"; args.append(desde)
    if hasta:
        filtro += " AND substr(e.inicio, 1, 10) <= ?"; args.append(hasta)
    eventos = con.execute(
        "SELECT e.*, (SELECT count(*) FROM pronosticos p WHERE p.evento_id = e.id AND p.estado <> 'Anulado') AS pronosticos, "
        "(SELECT count(*) FROM pronosticos p WHERE p.evento_id = e.id AND p.estado = 'Acertado') AS aciertos, "
        "(SELECT coalesce(sum(p.costo), 0) FROM pronosticos p WHERE p.evento_id = e.id AND p.estado <> 'Anulado') AS usados, "
        "(SELECT coalesce(sum(m.valor), 0) FROM movimientos m WHERE m.evento_id = e.id AND m.tipo = 'PREMIO') AS premios "
        f"FROM eventos e WHERE e.torneo_id = ?{filtro} ORDER BY e.inicio", args).fetchall()
    tot = {k: sum(e[k] for e in eventos) for k in ("pronosticos", "aciertos", "usados", "premios")}
    ids = [e["id"] for e in eventos] or [0]
    mq = ",".join("?" * len(ids))
    usados_mov = -con.execute(f"SELECT coalesce(sum(valor), 0) FROM movimientos WHERE tipo = 'PRONOSTICO' AND evento_id IN ({mq})", ids).fetchone()[0] \
        - con.execute(f"SELECT coalesce(sum(valor), 0) FROM movimientos WHERE tipo = 'REINTEGRO' AND evento_id IN ({mq})", ids).fetchone()[0]
    verificado = usados_mov == tot["usados"]
    return {"torneo": t, "eventos": eventos, "totales": tot, "liquidados": sum(1 for e in eventos if e["liquidado_en"]), "verificado": verificado}
