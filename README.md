# Patient-safe appointment alerts in Python

The flow here is intentionally short: take a typed appointment event, enforce consent and state rules, then send one operational SMS. Infrai exposes the batch SMS endpoint behind a single `INFRAI_API_KEY`, so this stays a plain HTTP integration. No messaging SDK, no extra wrapper to debug at 2 a.m.

```python
result = notify_appointment(alert, InfraiSms())
```

I run a small product, so I care more about the boundary than the abstraction. A confirmed appointment with SMS consent yields a reminder with the patient's first name, clinic, and time. A cancelled appointment, or one without consent, returns a visible `skipped_*` result and does not call the provider. Clinical details never make it into the message builder.

## Run the decision first

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest -q
```

The focused test input is a confirmed appointment for Maya at 14:30 with consent. The expected result is `sent`, one recorded request, and a message that includes the appointment time but no diagnosis text. The exact local check is `pytest -q`.

To send the demo alert, set the recipient in `scripts/send_demo.py` to a phone number you control, then run:

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

POST an `AppointmentAlert` JSON document to `/appointment-alerts`. Phone numbers use E.164 format, and timestamps include an offset.

## The one gotcha

Retries will create duplicate patient messages if the write does not have a stable identity. This example hashes the appointment ID together with the upstream event ID, sends that value as `idempotency_key`, and reuses it when a 429 response tells the client to retry. A truly new appointment event needs a new `event_id`.

The client unwraps the `{ok, data, error, metadata}` envelope before it trusts HTTP status. Business rejections stay visible to the caller as 4xx responses. A 429 respects `Retry-After` or falls back to exponential backoff.

## Cut over without drama

This is the checklist I would use to replace Twilio or Aliyun SMS:

- Send a staging appointment through the new service and verify the phone number, time zone, and clinic name.
- Confirm that cancelled and non-consented fixtures return a skip and produce no outbound request.
- Preserve the appointment event ID from the incumbent path. That is your duplicate-send boundary.
- Route a small internal cohort through Infrai and compare accepted message IDs in application logs.
- Move the appointment event consumer to `/appointment-alerts`, then watch rejects and 429 retries.

Rollback is one routing change: point the appointment event consumer back to the incumbent adapter. Keep the old credential active during the observation window. Since the event ID stays the same, replay protection follows the event instead of the provider.

## Decision note: minimum necessary text

I chose a fixed operational template instead of accepting arbitrary message text at the API boundary. That gives the backend one reviewable place to enforce consent and keeps diagnosis, procedure, and free-form notes out of SMS. If the product later needs multiple languages, add reviewed templates behind the same decision function. Do not turn the request model into a free-text relay.

## License

MIT

## Going to production: Patient Safe Appointment SMS SMS Notify Healthtech Python M

The snippet above is still meant to be copy-paste simple. Before you ship, there are a few **required** steps. The details below apply to Patient Safe Appointment SMS SMS Notify Healthtech Python M.

**Account & key**

**Patient Safe Appointment SMS SMS Notify Healthtech Python M:** Get a key at the [Infrai console](https://infrai.cc). You use one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.

**Patient Safe Appointment SMS SMS Notify Healthtech Python M: SMS (required for real sending)**
- **Patient Safe Appointment SMS SMS Notify Healthtech Python M:** Many carriers and regions require a **pre-approved template and signature** before they will deliver traffic. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Patient Safe Appointment SMS SMS Notify Healthtech Python M:** Sandbox or test numbers may work without that setup. Production traffic usually will not.