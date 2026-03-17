from __future__ import annotations

from datetime import datetime

import dateparser
from flask import Flask, jsonify, request

from appointment_store import Appointment, AppointmentStore
from notification_service import NotificationService


app = Flask(__name__)
store = AppointmentStore()
notifications = NotificationService()


def _parse_datetime(value: str) -> datetime | None:
    parsed = dateparser.parse(value, settings={"PREFER_DATES_FROM": "future"})
    return parsed


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


@app.post("/appointments/confirm")
def confirm_appointment() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}

    customer_name = str(payload.get("customer_name", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    appointment_at_text = str(payload.get("appointment_at", "")).strip()
    reason = str(payload.get("reason", "")).strip()
    confirmed = bool(payload.get("confirmed", False))

    if not customer_name or not phone or not appointment_at_text or not reason:
        return jsonify({"error": "Missing required fields"}), 400

    if not confirmed:
        return jsonify({"status": "not_confirmed", "saved": False}), 200

    appointment_at = _parse_datetime(appointment_at_text)
    if appointment_at is None:
        return jsonify({"error": "Could not parse appointment_at"}), 400

    appt = Appointment(
        customer_name=customer_name,
        phone=phone,
        appointment_at_iso=appointment_at.isoformat(),
        reason=reason,
    )
    appointment_id = store.create_appointment(appt)
    results = notifications.send_confirmation(appointment_id, appt)

    return (
        jsonify(
            {
                "status": "confirmed",
                "saved": True,
                "appointment_id": appointment_id,
                "notifications": [
                    {"channel": item.channel, "ok": item.ok, "detail": item.detail}
                    for item in results
                ],
            }
        ),
        201,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
