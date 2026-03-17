from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from typing import List

from appointment_store import Appointment


@dataclass
class NotificationResult:
    channel: str
    ok: bool
    detail: str


class NotificationService:
    def __init__(self) -> None:
        self.email_to = os.getenv("NOTIFY_EMAIL_TO", "").strip()
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        self.smtp_from = os.getenv("SMTP_FROM", self.smtp_username).strip()
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "1").strip() == "1"

        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        self.twilio_from = os.getenv("TWILIO_FROM_NUMBER", "").strip()

    def send_confirmation(self, appointment_id: int, appointment: Appointment) -> List[NotificationResult]:
        results: List[NotificationResult] = []
        results.append(self._send_email(appointment_id, appointment))
        results.append(self._send_sms(appointment_id, appointment))
        return results

    @staticmethod
    def _format_message(appointment_id: int, appointment: Appointment) -> str:
        when = datetime.fromisoformat(appointment.appointment_at_iso)
        when_text = when.strftime("%A, %B %d %Y at %I:%M %p")
        return (
            f"Appointment #{appointment_id} confirmed. "
            f"Customer: {appointment.customer_name}. "
            f"Phone: {appointment.phone}. "
            f"When: {when_text}. "
            f"Reason: {appointment.reason}."
        )

    def _send_email(self, appointment_id: int, appointment: Appointment) -> NotificationResult:
        if not (self.email_to and self.smtp_host and self.smtp_from):
            return NotificationResult("email", False, "Email config not set")

        message_text = self._format_message(appointment_id, appointment)
        email = EmailMessage()
        email["Subject"] = f"Appointment Confirmed #{appointment_id}"
        email["From"] = self.smtp_from
        email["To"] = self.email_to
        email.set_content(message_text)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=20) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(email)
            return NotificationResult("email", True, f"Sent to {self.email_to}")
        except Exception as exc:
            return NotificationResult("email", False, f"Email failed: {exc}")

    def _send_sms(self, appointment_id: int, appointment: Appointment) -> NotificationResult:
        if not (self.twilio_sid and self.twilio_token and self.twilio_from):
            return NotificationResult("sms", False, "Twilio config not set")

        try:
            from twilio.rest import Client
        except Exception as exc:
            return NotificationResult("sms", False, f"Twilio SDK missing: {exc}")

        to_number = appointment.phone
        if len(to_number) == 10:
            to_number = f"+1{to_number}"

        message_text = self._format_message(appointment_id, appointment)
        try:
            client = Client(self.twilio_sid, self.twilio_token)
            client.messages.create(body=message_text, from_=self.twilio_from, to=to_number)
            return NotificationResult("sms", True, f"Sent to {to_number}")
        except Exception as exc:
            return NotificationResult("sms", False, f"SMS failed: {exc}")
