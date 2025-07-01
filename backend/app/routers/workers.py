from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Worker])
def get_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all workers"""
    workers = db.query(models.Worker).offset(skip).limit(limit).all()
    return workers

@router.get("/{worker_id}", response_model=schemas.Worker)
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    """Get a specific worker by ID"""
    worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

@router.post("/", response_model=schemas.Worker, status_code=status.HTTP_201_CREATED)
def create_worker(worker: schemas.WorkerCreate, db: Session = Depends(get_db)):
    """Create a new worker"""
    # Check if email already exists
    existing_worker = db.query(models.Worker).filter(models.Worker.email == worker.email).first()
    if existing_worker:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_worker = models.Worker(**worker.dict())
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker

@router.put("/{worker_id}", response_model=schemas.Worker)
def update_worker(worker_id: int, worker_update: schemas.WorkerUpdate, db: Session = Depends(get_db)):
    """Update a worker"""
    worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Check if email is being updated and if it already exists
    if worker_update.email and worker_update.email != worker.email:
        existing_worker = db.query(models.Worker).filter(models.Worker.email == worker_update.email).first()
        if existing_worker:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    update_data = worker_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(worker, field, value)
    
    db.commit()
    db.refresh(worker)
    return worker

@router.delete("/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    """Delete a worker (soft delete by setting is_active to False)"""
    worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    worker.is_active = False
    db.commit()
    return {"message": "Worker deactivated successfully"}

@router.get("/{worker_id}/stats", response_model=schemas.WorkerStats)
def get_worker_stats(worker_id: int, db: Session = Depends(get_db)):
    """Get worker statistics"""
    worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Calculate statistics (simplified for now)
    # In a real implementation, you'd calculate based on actual time records
    stats = schemas.WorkerStats(
        worker_id=worker.id,
        worker_name=worker.name,
        total_hours_week=40.0,
        total_hours_month=160.0,
        overtime_hours_week=5.0,
        overtime_hours_month=20.0,
        shifts_completed_week=5,
        shifts_completed_month=20
    )
    return stats 