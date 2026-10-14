from datetime import datetime, timezone

from appointment_alerts.appointment_notifier import notify_appointment
from appointment_alerts.models import AppointmentAlert, AppointmentState


class RecordingSms:
    def __init__(self) -> None:
        self.calls: list[tuple[list[dict[str, str]], str]] = []

    def batch_send(
        self, messages: list[dict[str, str]], idempotency_key: str
    ) -> dict[str, str]:
        self.calls.append((messages, idempotency_key))
        return {"message_id": "msg_appointment_1"}


def appointment(**changes: object) -> AppointmentAlert:
    values = {
        "appointment_id": "apt_42",
        "event_id": "confirmation_1",
        "patient_phone": "+15551234567",
        "patient_first_name": "Maya",
        "starts_at": datetime(2026, 10, 3, 14, 30, tzinfo=timezone.utc),
        "clinic_name": "Harbor Family Clinic",
        "state": AppointmentState.CONFIRMED,
        "sms_consent": True,
    }
    values.update(changes)
    return AppointmentAlert(**values)


def test_confirmed_consented_appointment_sends_minimum_safe_detail() -> None:
    sms = RecordingSms()

    result = notify_appointment(appointment(), sms)  # type: ignore[arg-type]

    assert result.disposition == "sent"
    assert result.message_id == "msg_appointment_1"
    assert len(sms.calls) == 1
    message = sms.calls[0][0][0]
    assert message["to"] == "+15551234567"
    assert "Oct 03 at 14:30" in message["body"]
    assert "diagnosis" not in message["body"].lower()


def test_no_consent_is_a_visible_skip_without_api_call() -> None:
    sms = RecordingSms()

    result = notify_appointment(
        appointment(sms_consent=False), sms  # type: ignore[arg-type]
    )

    assert result.disposition == "skipped_no_consent"
    assert sms.calls == []


def test_same_event_produces_same_idempotency_key() -> None:
    sms = RecordingSms()

    notify_appointment(appointment(), sms)  # type: ignore[arg-type]
    notify_appointment(appointment(), sms)  # type: ignore[arg-type]

    assert sms.calls[0][1] == sms.calls[1][1]
