import sqlite3
from contextlib import contextmanager

DB_PATH = "purchases.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS people (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS payment_methods (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK(type IN ('credit_card', 'person_debt'))
            );

            CREATE TABLE IF NOT EXISTS purchases (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                description         TEXT    NOT NULL,
                purchase_date       TEXT,
                total_amount        REAL    NOT NULL,
                num_installments    INTEGER NOT NULL DEFAULT 1,
                first_payment_month INTEGER NOT NULL,
                first_payment_year  INTEGER NOT NULL,
                payment_method_id   INTEGER NOT NULL REFERENCES payment_methods(id),
                owner_participates  INTEGER NOT NULL DEFAULT 1,
                created_at          TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS purchase_participants (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL REFERENCES purchases(id) ON DELETE CASCADE,
                person_id   INTEGER NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
                UNIQUE(purchase_id, person_id)
            );
        """)
