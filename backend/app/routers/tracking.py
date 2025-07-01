from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/clock-in", response_model=schemas.TimeRecord, status_code=status.HTTP_201_CREATED)
def clock_in(time_record: schemas.TimeRecordCreate, db: Session = Depends(get_db)):
    """Clock in a worker"""
    # Verify worker exists
    worker = db.query(models.Worker).filter(models.Worker.id == time_record.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Check if worker is already clocked in
    active_record = db.query(models.TimeRecord).filter(
        models.TimeRecord.worker_id == time_record.worker_id,
        models.TimeRecord.status == "active"
    ).first()
    
    if active_record:
        raise HTTPException(status_code=400, detail="Worker is already clocked in")
    
    # Create new time record
    db_record = models.TimeRecord(
        worker_id=time_record.worker_id,
        shift_id=time_record.shift_id,
        clock_in=datetime.now(),
        notes=time_record.notes,
        status="active"
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.put("/clock-out/{record_id}", response_model=schemas.TimeRecord)
def clock_out(record_id: int, db: Session = Depends(get_db)):
    """Clock out a worker"""
    record = db.query(models.TimeRecord).filter(models.TimeRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Time record not found")
    
    if record.status != "active":
        raise HTTPException(status_code=400, detail="Time record is not active")
    
    # Update record with clock out time
    record.clock_out = datetime.now()
    record.status = "completed"
    
    # Calculate total hours
    if record.clock_in and record.clock_out:
        total_time = record.clock_out - record.clock_in
        
        # Subtract break time if exists
        if record.break_start and record.break_end:
            break_time = record.break_end - record.break_start
            total_time -= break_time
        
        record.total_hours = total_time.total_seconds() / 3600
        
        # Calculate overtime (assuming 8 hours is standard)
        if record.total_hours > 8:
            record.overtime_hours = record.total_hours - 8
    
    db.commit()
    db.refresh(record)
    return record

@router.put("/break-start/{record_id}", response_model=schemas.TimeRecord)
def start_break(record_id: int, db: Session = Depends(get_db)):
    """Start break for a worker"""
    record = db.query(models.TimeRecord).filter(models.TimeRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Time record not found")
    
    if record.status != "active":
        raise HTTPException(status_code=400, detail="Time record is not active")
    
    if record.break_start:
        raise HTTPException(status_code=400, detail="Break already started")
    
    record.break_start = datetime.now()
    db.commit()
    db.refresh(record)
    return record

@router.put("/break-end/{record_id}", response_model=schemas.TimeRecord)
def end_break(record_id: int, db: Session = Depends(get_db)):
    """End break for a worker"""
    record = db.query(models.TimeRecord).filter(models.TimeRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Time record not found")
    
    if not record.break_start:
        raise HTTPException(status_code=400, detail="Break not started")
    
    if record.break_end:
        raise HTTPException(status_code=400, detail="Break already ended")
    
    record.break_end = datetime.now()
    db.commit()
    db.refresh(record)
    return record

@router.get("/active", response_model=List[schemas.TimeRecord])
def get_active_records(db: Session = Depends(get_db)):
    """Get all active time records (workers currently clocked in)"""
    records = db.query(models.TimeRecord).filter(
        models.TimeRecord.status == "active"
    ).all()
    return records

@router.get("/worker/{worker_id}/active", response_model=schemas.TimeRecord)
def get_worker_active_record(worker_id: int, db: Session = Depends(get_db)):
    """Get active time record for a specific worker"""
    record = db.query(models.TimeRecord).filter(
        models.TimeRecord.worker_id == worker_id,
        models.TimeRecord.status == "active"
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="No active time record found for this worker")
    
    return record

@router.get("/records", response_model=List[schemas.TimeRecord])
def get_time_records(
    skip: int = 0, 
    limit: int = 100, 
    worker_id: int = None,
    db: Session = Depends(get_db)
):
    """Get time records with optional filtering"""
    query = db.query(models.TimeRecord)
    
    if worker_id:
        query = query.filter(models.TimeRecord.worker_id == worker_id)
    
    records = query.offset(skip).limit(limit).all()
    return records

@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    # Count total workers
    total_workers = db.query(models.Worker).count()
    
    # Count active workers
    active_workers = db.query(models.Worker).filter(models.Worker.is_active == True).count()
    
    # Count today's shifts
    today = datetime.now().date()
    total_shifts_today = db.query(models.Shift).filter(
        models.Shift.date == today
    ).count()
    
    # Count workers currently clocked in
    workers_clocked_in = db.query(models.TimeRecord).filter(
        models.TimeRecord.status == "active"
    ).count()
    
    # Calculate total hours today (simplified)
    today_records = db.query(models.TimeRecord).filter(
        models.TimeRecord.clock_in >= datetime.combine(today, datetime.min.time())
    ).all()
    
    total_hours_today = sum(record.total_hours or 0 for record in today_records)
    overtime_hours_today = sum(record.overtime_hours or 0 for record in today_records)
    
    return schemas.DashboardStats(
        total_workers=total_workers,
        active_workers=active_workers,
        total_shifts_today=total_shifts_today,
        workers_clocked_in=workers_clocked_in,
        total_hours_today=total_hours_today,
        overtime_hours_today=overtime_hours_today
    ) 