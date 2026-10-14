from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AppointmentState(StrEnum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class AppointmentAlert(BaseModel):
    appointment_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    patient_phone: str = Field(pattern=r"^\+[1-9]\d{7,14}$")
    patient_first_name: str = Field(min_length=1, max_length=40)
    starts_at: datetime
    clinic_name: str = Field(min_length=1, max_length=80)
    state: AppointmentState
    sms_consent: bool


class NotificationResult(BaseModel):
    appointment_id: str
    disposition: str
    message_id: str | None = None
