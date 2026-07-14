from typing import Literal

from pydantic import BaseModel, Field

PeriodName = Literal["Morning", "Evening"]
MedicationName = Literal["C1", "C2", "C3", "C4", "C5", "C6", "C7"]


class ScheduleEntry(BaseModel):
    medication: MedicationName
    morning: bool = False
    evening: bool = False


class PeriodDispense(BaseModel):
    period: PeriodName
    medications: list[MedicationName] = Field(default_factory=list)
