from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Shift])
def get_shifts(
    skip: int = 0, 
    limit: int = 100, 
    worker_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get shifts with optional filtering"""
    query = db.query(models.Shift).options(joinedload(models.Shift.worker))
    
    if worker_id:
        query = query.filter(models.Shift.worker_id == worker_id)
    
    if date_from:
        query = query.filter(models.Shift.date >= date_from)
    
    if date_to:
        query = query.filter(models.Shift.date <= date_to)
    
    if status:
        query = query.filter(models.Shift.status == status)
    
    shifts = query.offset(skip).limit(limit).all()
    return shifts

@router.get("/{shift_id}", response_model=schemas.Shift)
def get_shift(shift_id: int, db: Session = Depends(get_db)):
    """Get a specific shift by ID"""
    shift = db.query(models.Shift).options(joinedload(models.Shift.worker)).filter(models.Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift

@router.post("/", response_model=schemas.Shift, status_code=status.HTTP_201_CREATED)
def create_shift(shift: schemas.ShiftCreate, db: Session = Depends(get_db)):
    """Create a new shift"""
    # Verify worker exists
    worker = db.query(models.Worker).filter(models.Worker.id == shift.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Check for overlapping shifts
    overlapping_shift = db.query(models.Shift).filter(
        models.Shift.worker_id == shift.worker_id,
        models.Shift.date == shift.date,
        models.Shift.status != "cancelled"
    ).first()
    
    if overlapping_shift:
        raise HTTPException(
            status_code=400, 
            detail="Worker already has a shift scheduled for this date"
        )
    
    db_shift = models.Shift(**shift.dict())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    
    # Reload with worker information
    shift_with_worker = db.query(models.Shift).options(joinedload(models.Shift.worker)).filter(models.Shift.id == db_shift.id).first()
    return shift_with_worker

@router.put("/{shift_id}", response_model=schemas.Shift)
def update_shift(shift_id: int, shift_update: schemas.ShiftUpdate, db: Session = Depends(get_db)):
    """Update a shift"""
    shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    update_data = shift_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shift, field, value)
    
    db.commit()
    db.refresh(shift)
    
    # Reload with worker information
    shift_with_worker = db.query(models.Shift).options(joinedload(models.Shift.worker)).filter(models.Shift.id == shift_id).first()
    return shift_with_worker

@router.delete("/{shift_id}")
def delete_shift(shift_id: int, db: Session = Depends(get_db)):
    """Delete a shift"""
    shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    db.delete(shift)
    db.commit()
    return {"message": "Shift deleted successfully"}

@router.get("/today/", response_model=List[schemas.Shift])
def get_today_shifts(db: Session = Depends(get_db)):
    """Get all shifts for today"""
    today = date.today()
    shifts = db.query(models.Shift).options(joinedload(models.Shift.worker)).filter(
        models.Shift.date == today
    ).all()
    return shifts

@router.get("/worker/{worker_id}/upcoming", response_model=List[schemas.Shift])
def get_worker_upcoming_shifts(worker_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Get upcoming shifts for a specific worker"""
    worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    today = date.today()
    shifts = db.query(models.Shift).options(joinedload(models.Shift.worker)).filter(
        models.Shift.worker_id == worker_id,
        models.Shift.date >= today,
        models.Shift.status == "scheduled"
    ).order_by(models.Shift.date).limit(limit).all()
    
    return shifts 