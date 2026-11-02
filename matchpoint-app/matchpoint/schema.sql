-- MatchPoint · Esquema de base de datos (Sprint 1)
-- SQLite. Los créditos son virtuales: no tienen valor monetario.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario         TEXT    NOT NULL UNIQUE,
    correo          TEXT    NOT NULL UNIQUE,
    nombre          TEXT    NOT NULL,
    clave_hash      TEXT    NOT NULL,
    rol             TEXT    NOT NULL CHECK (rol IN ('admin', 'participante')),
    activo          INTEGER NOT NULL DEFAULT 1,
    saldo           INTEGER NOT NULL DEFAULT 0 CHECK (saldo >= 0),   -- HU008/HU010: nunca negativo
    creado_en       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS configuracion (
    clave   TEXT PRIMARY KEY,
    valor   TEXT NOT NULL
);

-- HU009 / HU010: cada cambio de saldo queda como movimiento trazable
CREATE TABLE IF NOT EXISTS movimientos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    tipo            TEXT    NOT NULL CHECK (tipo IN ('ASIGNACION_INICIAL', 'PRONOSTICO', 'PREMIO', 'REINTEGRO', 'AJUSTE')),
    valor           INTEGER NOT NULL,          -- negativo = cargo, positivo = abono
    saldo_resultante INTEGER NOT NULL CHECK (saldo_resultante >= 0),
    detalle         TEXT    NOT NULL,
    origen          TEXT,                       -- referencia al registro que lo originó (p. ej. P-0001)
    creado_en       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
-- HU009 paso 3: la asignación inicial solo puede existir una vez por participante
CREATE UNIQUE INDEX IF NOT EXISTS ux_asignacion_inicial
    ON movimientos (usuario_id) WHERE tipo = 'ASIGNACION_INICIAL';

CREATE TABLE IF NOT EXISTS torneos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL,
    deporte         TEXT    NOT NULL,
    fecha_inicio    TEXT    NOT NULL,           -- YYYY-MM-DD
    fecha_fin       TEXT    NOT NULL,
    descripcion     TEXT    NOT NULL DEFAULT '',
    estado          TEXT    NOT NULL DEFAULT 'Programado' CHECK (estado IN ('Programado', 'En curso', 'Finalizado', 'Cancelado')),
    creado_en       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    CHECK (fecha_fin >= fecha_inicio),
    UNIQUE (nombre, fecha_inicio, fecha_fin)    -- HU003 paso 3
);

-- HU004 paso 6: historial de cambios del torneo
CREATE TABLE IF NOT EXISTS cambios_torneo (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    torneo_id       INTEGER NOT NULL REFERENCES torneos(id) ON DELETE CASCADE,
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    descripcion     TEXT    NOT NULL,
    creado_en       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS eventos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    torneo_id       INTEGER NOT NULL REFERENCES torneos(id) ON DELETE RESTRICT,  -- HU005 paso 6
    local           TEXT    NOT NULL,
    visitante       TEXT    NOT NULL,
    inicio          TEXT    NOT NULL,           -- YYYY-MM-DDTHH:MM
    cierre          TEXT    NOT NULL,           -- fecha límite para pronosticar
    costo           INTEGER NOT NULL CHECK (costo > 0),
    premio          INTEGER NOT NULL CHECK (premio > 0),
    estado          TEXT    NOT NULL DEFAULT 'Abierto' CHECK (estado IN ('Abierto', 'Cerrado', 'Finalizado')),
    creado_en       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    CHECK (lower(local) <> lower(visitante)),   -- HU006 paso 4
    CHECK (cierre < inicio)                     -- HU006 paso 3
);

CREATE TABLE IF NOT EXISTS pronosticos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id       INTEGER NOT NULL REFERENCES eventos(id),
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    opcion          TEXT    NOT NULL CHECK (opcion IN ('LOCAL', 'EMPATE', 'VISITANTE')),
    costo           INTEGER NOT NULL,
    estado          TEXT    NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Acertado', 'No acertado', 'Anulado')),
    solicitud_id    TEXT    NOT NULL UNIQUE,    -- HU008 paso 5: idempotencia
    creado_en       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (evento_id, usuario_id)              -- HU008 paso 2: un pronóstico por evento
);
