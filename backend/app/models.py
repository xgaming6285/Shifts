from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    position = Column(String(100))
    hourly_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    shifts = relationship("Shift", back_populates="worker")
    time_records = relationship("TimeRecord", back_populates="worker")

class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # daily, weekly, monthly
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    worker = relationship("Worker", back_populates="shifts")
    time_records = relationship("TimeRecord", back_populates="shift")

class TimeRecord(Base):
    __tablename__ = "time_records"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    clock_in = Column(DateTime, nullable=False)
    clock_out = Column(DateTime, nullable=True)
    break_start = Column(DateTime, nullable=True)
    break_end = Column(DateTime, nullable=True)
    total_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    status = Column(String(20), default="active")  # active, completed
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    worker = relationship("Worker", back_populates="time_records")
    shift = relationship("Shift", back_populates="time_records")

class Holiday(Base):
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 