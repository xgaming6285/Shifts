from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import io
from datetime import datetime, date
from app.database import get_db
from app import models, schemas
from app.services.google_sheets_service import GoogleSheetsService

router = APIRouter()

@router.post("/export")
async def export_to_google_sheets(
    export_data: schemas.GoogleSheetsExport,
    db: Session = Depends(get_db)
):
    """Export shift data to Google Sheets"""
    try:
        # Get data based on filters
        query = db.query(models.TimeRecord).join(models.Worker)
        
        if export_data.worker_ids:
            query = query.filter(models.TimeRecord.worker_id.in_(export_data.worker_ids))
        
        if export_data.date_from:
            query = query.filter(models.TimeRecord.clock_in >= export_data.date_from)
        
        if export_data.date_to:
            query = query.filter(models.TimeRecord.clock_in <= export_data.date_to)
        
        records = query.all()
        
        # Prepare data for export
        export_records = []
        for record in records:
            export_records.append({
                'Worker Name': record.worker.name,
                'Worker Email': record.worker.email,
                'Position': record.worker.position,
                'Clock In': record.clock_in.strftime('%Y-%m-%d %H:%M:%S') if record.clock_in else '',
                'Clock Out': record.clock_out.strftime('%Y-%m-%d %H:%M:%S') if record.clock_out else '',
                'Break Start': record.break_start.strftime('%Y-%m-%d %H:%M:%S') if record.break_start else '',
                'Break End': record.break_end.strftime('%Y-%m-%d %H:%M:%S') if record.break_end else '',
                'Total Hours': record.total_hours or 0,
                'Overtime Hours': record.overtime_hours or 0,
                'Status': record.status,
                'Notes': record.notes or ''
            })
        
        # Use Google Sheets service to export
        sheets_service = GoogleSheetsService()
        result = await sheets_service.export_data(
            data=export_records,
            spreadsheet_id=export_data.spreadsheet_id,
            sheet_name=export_data.sheet_name
        )
        
        return {
            "message": "Data exported successfully",
            "spreadsheet_id": result.get("spreadsheet_id"),
            "sheet_url": result.get("sheet_url"),
            "records_exported": len(export_records)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/import")
async def import_from_google_sheets(
    import_data: schemas.GoogleSheetsImport,
    db: Session = Depends(get_db)
):
    """Import shift data from Google Sheets"""
    try:
        sheets_service = GoogleSheetsService()
        data = await sheets_service.import_data(
            spreadsheet_id=import_data.spreadsheet_id,
            sheet_name=import_data.sheet_name,
            range_name=import_data.range_name
        )
        
        imported_count = 0
        errors = []
        
        for row_data in data:
            try:
                # Find or create worker
                worker_email = row_data.get('Worker Email')
                if not worker_email:
                    errors.append(f"Missing worker email in row: {row_data}")
                    continue
                
                worker = db.query(models.Worker).filter(
                    models.Worker.email == worker_email
                ).first()
                
                if not worker:
                    # Create new worker
                    worker = models.Worker(
                        name=row_data.get('Worker Name', ''),
                        email=worker_email,
                        position=row_data.get('Position', '')
                    )
                    db.add(worker)
                    db.commit()
                    db.refresh(worker)
                
                # Create time record
                clock_in_str = row_data.get('Clock In')
                if clock_in_str:
                    clock_in = datetime.strptime(clock_in_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Check if record already exists
                    existing_record = db.query(models.TimeRecord).filter(
                        models.TimeRecord.worker_id == worker.id,
                        models.TimeRecord.clock_in == clock_in
                    ).first()
                    
                    if not existing_record:
                        time_record = models.TimeRecord(
                            worker_id=worker.id,
                            clock_in=clock_in,
                            clock_out=datetime.strptime(row_data.get('Clock Out'), '%Y-%m-%d %H:%M:%S') if row_data.get('Clock Out') else None,
                            total_hours=float(row_data.get('Total Hours', 0)),
                            overtime_hours=float(row_data.get('Overtime Hours', 0)),
                            status=row_data.get('Status', 'completed'),
                            notes=row_data.get('Notes', '')
                        )
                        db.add(time_record)
                        imported_count += 1
                
            except Exception as e:
                errors.append(f"Error processing row {row_data}: {str(e)}")
        
        db.commit()
        
        return {
            "message": "Import completed",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and import data from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Find or create worker
                worker_email = row.get('Worker Email') or row.get('email')
                if pd.isna(worker_email):
                    errors.append(f"Missing worker email in row {index + 1}")
                    continue
                
                worker = db.query(models.Worker).filter(
                    models.Worker.email == worker_email
                ).first()
                
                if not worker:
                    worker = models.Worker(
                        name=row.get('Worker Name') or row.get('name', ''),
                        email=worker_email,
                        position=row.get('Position') or row.get('position', ''),
                        hourly_rate=float(row.get('Hourly Rate') or row.get('hourly_rate', 0))
                    )
                    db.add(worker)
                    db.commit()
                    db.refresh(worker)
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error processing row {index + 1}: {str(e)}")
        
        db.commit()
        
        return {
            "message": "CSV imported successfully",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV import failed: {str(e)}")

@router.get("/export-csv")
async def export_to_csv(
    worker_id: int = None,
    date_from: date = None,
    date_to: date = None,
    db: Session = Depends(get_db)
):
    """Export data to CSV format"""
    try:
        query = db.query(models.TimeRecord).join(models.Worker)
        
        if worker_id:
            query = query.filter(models.TimeRecord.worker_id == worker_id)
        
        if date_from:
            query = query.filter(models.TimeRecord.clock_in >= date_from)
        
        if date_to:
            query = query.filter(models.TimeRecord.clock_in <= date_to)
        
        records = query.all()
        
        # Prepare data for CSV
        csv_data = []
        for record in records:
            csv_data.append({
                'Worker Name': record.worker.name,
                'Worker Email': record.worker.email,
                'Position': record.worker.position,
                'Hourly Rate': record.worker.hourly_rate,
                'Clock In': record.clock_in.strftime('%Y-%m-%d %H:%M:%S') if record.clock_in else '',
                'Clock Out': record.clock_out.strftime('%Y-%m-%d %H:%M:%S') if record.clock_out else '',
                'Total Hours': record.total_hours or 0,
                'Overtime Hours': record.overtime_hours or 0,
                'Status': record.status,
                'Notes': record.notes or ''
            })
        
        # Convert to CSV
        df = pd.DataFrame(csv_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        return {
            "csv_data": csv_buffer.getvalue(),
            "filename": f"shifts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}") 