from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ShiftStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TimeRecordStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"

# Worker Schemas
class WorkerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    position: Optional[str] = None
    hourly_rate: Optional[float] = 0.0
    is_active: Optional[bool] = True

class WorkerCreate(WorkerBase):
    pass

class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    hourly_rate: Optional[float] = None
    is_active: Optional[bool] = None

class Worker(WorkerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Shift Schemas
class ShiftBase(BaseModel):
    worker_id: int
    date: datetime
    start_time: datetime
    end_time: datetime
    is_recurring: Optional[bool] = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    status: Optional[ShiftStatus] = ShiftStatus.SCHEDULED
    notes: Optional[str] = None

class ShiftCreate(ShiftBase):
    pass

class ShiftUpdate(BaseModel):
    worker_id: Optional[int] = None
    date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    status: Optional[ShiftStatus] = None
    notes: Optional[str] = None

class Shift(ShiftBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    worker: Optional[Worker] = None
    
    class Config:
        from_attributes = True

# Time Record Schemas
class TimeRecordBase(BaseModel):
    worker_id: int
    shift_id: Optional[int] = None
    clock_in: datetime
    clock_out: Optional[datetime] = None
    break_start: Optional[datetime] = None
    break_end: Optional[datetime] = None
    total_hours: Optional[float] = 0.0
    overtime_hours: Optional[float] = 0.0
    status: Optional[TimeRecordStatus] = TimeRecordStatus.ACTIVE
    notes: Optional[str] = None

class TimeRecordCreate(BaseModel):
    worker_id: int
    shift_id: Optional[int] = None
    notes: Optional[str] = None

class TimeRecordUpdate(BaseModel):
    clock_out: Optional[datetime] = None
    break_start: Optional[datetime] = None
    break_end: Optional[datetime] = None
    notes: Optional[str] = None

class TimeRecord(TimeRecordBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    worker: Optional[Worker] = None
    shift: Optional[Shift] = None
    
    class Config:
        from_attributes = True

# Holiday Schemas
class HolidayBase(BaseModel):
    name: str
    date: datetime
    is_recurring: Optional[bool] = True

class HolidayCreate(HolidayBase):
    pass

class Holiday(HolidayBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Google Sheets Schemas
class GoogleSheetsExport(BaseModel):
    spreadsheet_id: Optional[str] = None
    sheet_name: str = "Shifts Data"
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    worker_ids: Optional[List[int]] = None

class GoogleSheetsImport(BaseModel):
    spreadsheet_id: str
    sheet_name: str = "Shifts Data"
    range_name: Optional[str] = None

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_workers: int
    active_workers: int
    total_shifts_today: int
    workers_clocked_in: int
    total_hours_today: float
    overtime_hours_today: float

class WorkerStats(BaseModel):
    worker_id: int
    worker_name: str
    total_hours_week: float
    total_hours_month: float
    overtime_hours_week: float
    overtime_hours_month: float
    shifts_completed_week: int
    shifts_completed_month: int 