from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import dateparser
import pyttsx3
import speech_recognition as sr

from appointment_store import Appointment, AppointmentStore
from notification_service import NotificationService


YES_WORDS = {"yes", "yeah", "yep", "confirm", "confirmed", "correct", "sounds good"}
NO_WORDS = {"no", "nope", "cancel", "stop", "wrong"}


@dataclass
class AppointmentDraft:
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    appointment_at: Optional[datetime] = None
    reason: Optional[str] = None


class VoiceAppointmentBot:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", 175)
        self.store = AppointmentStore()
        self.notifications = NotificationService()
        self.draft = AppointmentDraft()

    def speak(self, text: str) -> None:
        print(f"BOT: {text}")
        self.tts.say(text)
        self.tts.runAndWait()

    def listen(self) -> str:
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.7)
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=10)
            text = self.recognizer.recognize_google(audio)
            print(f"YOU: {text}")
            return text.strip()
        except Exception:
            typed = input("YOU (typed fallback): ").strip()
            return typed

    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        digits = re.sub(r"\D", "", text)
        if len(digits) >= 10:
            return digits[-10:]
        return None

    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        patterns = [
            r"(?:my name is|this is|i am|i'm)\s+([a-zA-Z\-\s]{2,50})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        if len(text.split()) <= 4 and re.fullmatch(r"[a-zA-Z\-\s]+", text):
            return text.strip().title()
        return None

    @staticmethod
    def _extract_datetime(text: str) -> Optional[datetime]:
        dt = dateparser.parse(text, settings={"PREFER_DATES_FROM": "future"})
        return dt

    @staticmethod
    def _contains_any(text: str, words: set[str]) -> bool:
        normalized = text.lower()
        return any(word in normalized for word in words)

    def _collect_missing_fields(self) -> None:
        if not self.draft.customer_name:
            self.speak("Can I get the customer's full name?")
            self.draft.customer_name = self._extract_name(self.listen())

        if not self.draft.phone:
            self.speak("Please tell me the best callback phone number.")
            self.draft.phone = self._extract_phone(self.listen())

        if not self.draft.appointment_at:
            self.speak("What date and time should I book the appointment for?")
            self.draft.appointment_at = self._extract_datetime(self.listen())

        if not self.draft.reason:
            self.speak("What is the reason for the appointment?")
            reason = self.listen()
            self.draft.reason = reason if reason else None

    def _all_fields_ready(self) -> bool:
        return all(
            [
                self.draft.customer_name,
                self.draft.phone,
                self.draft.appointment_at,
                self.draft.reason,
            ]
        )

    def _confirm_and_book(self) -> bool:
        assert self.draft.appointment_at is not None

        at_human = self.draft.appointment_at.strftime("%A %b %d at %I:%M %p")
        phone_tail = (self.draft.phone or "")[-4:] if self.draft.phone else "unknown"
        confirmation_prompt = (
            f"I have {self.draft.customer_name}, phone ending in {phone_tail}, "
            f"for {at_human}, reason: {self.draft.reason}. "
            "Should I confirm and create this appointment?"
        )

        self.speak(confirmation_prompt)
        response = self.listen().lower()
        if self._contains_any(response, YES_WORDS):
            appointment = Appointment(
                customer_name=self.draft.customer_name or "Unknown",
                phone=self.draft.phone or "",
                appointment_at_iso=self.draft.appointment_at.isoformat(),
                reason=self.draft.reason or "General",
            )
            appointment_id = self.store.create_appointment(appointment)
            notify_results = self.notifications.send_confirmation(appointment_id, appointment)
            notify_ok = [result.channel for result in notify_results if result.ok]
            self.speak(
                f"Done. Appointment {appointment_id} is confirmed and saved automatically."
            )
            if notify_ok:
                self.speak(f"Confirmation sent by: {', '.join(notify_ok)}.")
            return True

        if self._contains_any(response, NO_WORDS):
            self.speak("Okay, I cancelled that booking. Let's try again.")
            self.draft = AppointmentDraft()
            return False

        self.speak("I could not understand the confirmation. Please answer yes or no.")
        return False

    def run(self) -> None:
        self.speak(
            "Hello, I am your voice appointment assistant. "
            "I can collect customer details and auto book after confirmation."
        )
        while True:
            self.draft = AppointmentDraft()
            self._collect_missing_fields()

            if not self._all_fields_ready():
                self.speak("I am missing some details. Let's start over.")
                continue

            booked = self._confirm_and_book()
            if booked:
                self.speak("Do you want to create another appointment?")
                again = self.listen().lower()
                if not self._contains_any(again, YES_WORDS):
                    self.speak("Goodbye.")
                    break


if __name__ == "__main__":
    VoiceAppointmentBot().run()
