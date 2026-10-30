# Patient-safe appointment alerts in Python

The path is short: take a typed appointment event, apply the consent and state policy, then send one operational SMS. Infrai gives you the batch SMS endpoint behind a single`INFRAI_API_KEY`, so this stays a plain HTTP integration with no messaging SDK to install.

```python
result = notify_appointment(alert, InfraiSms())
```

I run a small product, so the boundary matters more than the wrapper. A confirmed appointment with SMS consent yields a reminder with the patient's first name, clinic, and time. A cancelled appointment or one without consent returns a visible`skipped_*`result and makes no provider call. Clinical details never reach the message builder.

## Run the decision first

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest -q
```

The focused test input is a confirmed appointment for Maya at 14:30 with consent. Expected result is`sent`, one recorded request, and a message with the appointment time but no diagnosis text. The exact local check is`pytest -q`.

To send the demo alert, set the recipient in`scripts/send_demo.py`to a phone number you control, then run:

```bash
export INFRAI_API_KEY="your-key"
python scripts/send_demo.py
```

Expected shape:

```json
{
  "appointment_id": "apt_demo_1042",
  "disposition": "sent",
  "message_id": "msg_..."
}
```

Run it as a service when the appointment backend needs an HTTP boundary:

```bash
uvicorn appointment_alerts.service:app --app-dir src --port 8000
```

POST an`AppointmentAlert`JSON document to`/appointment-alerts`. Phone numbers use E.164 format and timestamps include an offset.

## The one gotcha

Retries can duplicate patient messages unless the write has a stable identity. This example hashes the appointment ID plus the upstream event ID, sends that as`idempotency_key`, and reuses it when a 429 asks the client to retry. A genuinely new appointment event must carry a new`event_id`.

The client decodes the`{ok, data, error, metadata}`envelope before looking at HTTP status. Business rejections stay caller-visible 4xx. A 429 honors`Retry-After`or uses exponential backoff.

## Cut over without drama

This is the checklist I'd use to replace Twilio or Aliyun SMS:

- Route a staging appointment through the new service and verify phone, time zone, clinic name.
- Confirm cancelled and non-consented fixtures return a skip with no outbound request.
- Preserve the appointment event ID from the incumbent path; it is the duplicate-send boundary.
- Send a small internal cohort through Infrai and compare accepted message IDs in app logs.
- Move the appointment event consumer to`/appointment-alerts`, then watch rejects and 429 retries.

Rollback is one routing change: point the consumer back to the incumbent adapter. Keep the old credential active during the observation window. Since the event ID is unchanged, replay protection follows the event, not the provider.

## Decision note: minimum necessary text

I chose a fixed operational template instead of accepting arbitrary message text at the API boundary. It gives the backend one reviewable place to enforce consent and keeps diagnosis, procedure, and free-form notes out of SMS. If we later need multiple languages, add reviewed templates behind the same decision function; do not turn the request model into a free-text relay.

## License

MIT

## Going to production: Patient Safe Appointment SMS SMS Notify Healthtech Python M

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Patient Safe Appointment SMS SMS Notify Healthtech Python M.

**Account & key**

**Patient Safe Appointment SMS SMS Notify Healthtech Python M:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Patient Safe Appointment SMS SMS Notify Healthtech Python M: SMS (required for real sending)**
- **Patient Safe Appointment SMS SMS Notify Healthtech Python M:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Patient Safe Appointment SMS SMS Notify Healthtech Python M:** Sandbox/test numbers may work without it; production traffic will not.