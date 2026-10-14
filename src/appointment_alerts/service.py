from fastapi import FastAPI, HTTPException

from .appointment_notifier import notify_appointment
from .infrai_sms import InfraiError, InfraiSms
from .models import AppointmentAlert, NotificationResult

app = FastAPI(title="Appointment SMS alerts")


@app.post("/appointment-alerts", response_model=NotificationResult)
def send_appointment_alert(alert: AppointmentAlert) -> NotificationResult:
    sms = InfraiSms()
    try:
        return notify_appointment(alert, sms)
    except InfraiError as exc:
        caller_status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(
            status_code=caller_status,
            detail={"code": exc.code, "message": exc.detail.get("message")},
        ) from exc
    finally:
        sms.close()
