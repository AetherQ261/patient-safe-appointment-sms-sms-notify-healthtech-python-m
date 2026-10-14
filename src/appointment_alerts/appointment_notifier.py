import hashlib

from .infrai_sms import InfraiSms
from .models import AppointmentAlert, AppointmentState, NotificationResult


def notification_text(alert: AppointmentAlert) -> str:
    local_time = alert.starts_at.strftime("%b %d at %H:%M")
    return (
        f"Hi {alert.patient_first_name}, your appointment with "
        f"{alert.clinic_name} is confirmed for {local_time}. "
        "Call the clinic if you need to change it."
    )


def notify_appointment(alert: AppointmentAlert, sms: InfraiSms) -> NotificationResult:
    if not alert.sms_consent:
        return NotificationResult(
            appointment_id=alert.appointment_id, disposition="skipped_no_consent"
        )
    if alert.state is not AppointmentState.CONFIRMED:
        return NotificationResult(
            appointment_id=alert.appointment_id, disposition="skipped_not_confirmed"
        )

    stable_source = f"appointment:{alert.appointment_id}:event:{alert.event_id}"
    idempotency_key = hashlib.sha256(stable_source.encode()).hexdigest()
    data = sms.batch_send(
        messages=[{"to": alert.patient_phone, "body": notification_text(alert)}],
        idempotency_key=idempotency_key,
    )
    message_id = data.get("message_id")
    if message_id is None and data.get("messages"):
        message_id = data["messages"][0].get("message_id")
    return NotificationResult(
        appointment_id=alert.appointment_id,
        disposition="sent",
        message_id=str(message_id) if message_id else None,
    )
