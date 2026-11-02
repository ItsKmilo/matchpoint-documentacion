"""Acceso a SQLite: conexión por petición, creación del esquema y datos iniciales."""
import sqlite3
from pathlib import Path

from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = Path(__file__).with_name("schema.sql")


def connect(path):
    # isolation_level=None: controlamos las transacciones a mano (BEGIN IMMEDIATE ... COMMIT)
    con = sqlite3.connect(path, detect_types=0, isolation_level=None, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def close_db(_exc=None):
    con = g.pop("db", None)
    if con is not None:
        con.close()


class transaction:
    """Bloque atómico: todo se confirma junto o nada se aplica."""

    def __init__(self, con):
        self.con = con

    def __enter__(self):
        self.con.execute("BEGIN IMMEDIATE")
        return self.con

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.con.execute("COMMIT")
        else:
            self.con.execute("ROLLBACK")
        return False


def init_db(path, admin_user="admin", admin_password="admin123", initial_credits=1000):
    con = connect(path)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    con.execute("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('saldo_inicial', ?)", (str(initial_credits),))
    if not con.execute("SELECT 1 FROM usuarios WHERE rol = 'admin'").fetchone():
        con.execute(
            "INSERT INTO usuarios (usuario, correo, nombre, clave_hash, rol) VALUES (?, ?, ?, ?, 'admin')",
            (admin_user, "admin@matchpoint.local", "Administrador MatchPoint", generate_password_hash(admin_password)),
        )
    con.close()


def init_app(app):
    app.teardown_appcontext(close_db)
