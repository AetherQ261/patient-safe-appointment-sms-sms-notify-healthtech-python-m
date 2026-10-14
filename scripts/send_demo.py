from datetime import datetime, timedelta, timezone

from appointment_alerts.appointment_notifier import notify_appointment
from appointment_alerts.infrai_sms import InfraiSms
from appointment_alerts.models import AppointmentAlert, AppointmentState


alert = AppointmentAlert(
    appointment_id="apt_demo_1042",
    event_id="confirmed_v1",
    patient_phone="+15551234567",
    patient_first_name="Maya",
    starts_at=datetime.now(timezone.utc) + timedelta(days=1),
    clinic_name="Harbor Family Clinic",
    state=AppointmentState.CONFIRMED,
    sms_consent=True,
)

client = InfraiSms()
try:
    print(notify_appointment(alert, client).model_dump_json(indent=2))
finally:
    client.close()
