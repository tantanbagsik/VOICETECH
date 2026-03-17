from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Appointment:
    customer_name: str
    phone: str
    appointment_at_iso: str
    reason: str
    notes: str = ""


class AppointmentStore:
    def __init__(self, db_path: str = "appointments.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    appointment_at_iso TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def create_appointment(self, appointment: Appointment) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO appointments (
                    customer_name,
                    phone,
                    appointment_at_iso,
                    reason,
                    notes
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    appointment.customer_name,
                    appointment.phone,
                    appointment.appointment_at_iso,
                    appointment.reason,
                    appointment.notes,
                ),
            )
            conn.commit()
            row_id = cursor.lastrowid
            if row_id is None:
                raise RuntimeError("Failed to create appointment row")
            return int(row_id)

    def get_appointment(self, appointment_id: int) -> Optional[Appointment]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT customer_name, phone, appointment_at_iso, reason, notes
                FROM appointments
                WHERE id = ?
                """,
                (appointment_id,),
            ).fetchone()

        if not row:
            return None

        return Appointment(
            customer_name=row[0],
            phone=row[1],
            appointment_at_iso=row[2],
            reason=row[3],
            notes=row[4] or "",
        )
