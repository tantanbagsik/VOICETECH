# Voice Automation Appointment Bot

This project is a voice-enabled chatbot that:

- Listens to customer details (name, phone, date/time, reason)
- Repeats the appointment details for explicit confirmation
- Automatically creates and stores the appointment after confirmation
- Sends confirmation by SMS and/or email (when configured)

Appointments are persisted to a local SQLite database (`appointments.db`).

## Tech used

- `SpeechRecognition` for speech-to-text
- `pyttsx3` for text-to-speech
- `dateparser` for date/time extraction from natural language
- `sqlite3` (built-in) for appointment storage
- `twilio` for SMS confirmation (optional)

## Setup

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the bot:

```bash
python bot.py
```

You can also run an API test mode (no microphone required):

```bash
python api_server.py
```

## How booking works

1. The bot asks for customer details.
2. It generates a full booking summary.
3. If customer says yes/confirm, the bot writes the appointment into SQLite automatically.
4. If customer says no/cancel, the draft is discarded.

## Notes

- If microphone recognition fails, the bot falls back to typed input.
- For better microphone support on some systems, you may need additional OS audio dependencies.

## Optional confirmation channels

Set any of these environment variables to enable notifications after confirmation.

Email:

- `NOTIFY_EMAIL_TO`
- `SMTP_HOST`
- `SMTP_PORT` (default: `587`)
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM` (optional; defaults to username)
- `SMTP_USE_TLS` (`1` or `0`, default: `1`)

SMS (Twilio):

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER` (E.164 format, example: `+15551234567`)

If notification configuration is missing, booking still succeeds and is saved locally.

## Docker live test

This is the best way to run a live test endpoint.

1. Copy env file and set values (optional):

```bash
copy .env.example .env
```

2. Start container:

```bash
docker compose up --build
```

3. Health check:

```bash
curl http://localhost:8000/health
```

4. Confirm and auto-create appointment:

```bash
curl -X POST http://localhost:8000/appointments/confirm \
  -H "Content-Type: application/json" \
  -d "{\"customer_name\":\"John Doe\",\"phone\":\"+15551234567\",\"appointment_at\":\"tomorrow 3pm\",\"reason\":\"consultation\",\"confirmed\":true}"
```

The response includes `appointment_id` and notification status for email/SMS.
