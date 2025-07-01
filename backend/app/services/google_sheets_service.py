import os
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from datetime import datetime

class GoogleSheetsService:
    def __init__(self):
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets API service"""
        try:
            # Try to use service account credentials first
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            else:
                # Try to use credentials from environment variable
                credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
                if credentials_json:
                    credentials_info = json.loads(credentials_json)
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info,
                        scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                else:
                    # No credentials available - service will be limited
                    self.service = None
                    return
            
            self.service = build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            print(f"Failed to initialize Google Sheets service: {e}")
            self.service = None
    
    async def export_data(
        self, 
        data: List[Dict[str, Any]], 
        spreadsheet_id: Optional[str] = None,
        sheet_name: str = "Shifts Data"
    ) -> Dict[str, str]:
        """Export data to Google Sheets"""
        if not self.service:
            raise Exception("Google Sheets service not initialized. Please configure credentials.")
        
        try:
            # Create new spreadsheet if no ID provided
            if not spreadsheet_id:
                spreadsheet = {
                    'properties': {
                        'title': f'Shifts Export {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                    }
                }
                spreadsheet = self.service.spreadsheets().create(
                    body=spreadsheet,
                    fields='spreadsheetId'
                ).execute()
                spreadsheet_id = spreadsheet.get('spreadsheetId')
            
            # Prepare data for sheets
            if not data:
                return {
                    "spreadsheet_id": spreadsheet_id,
                    "sheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
                    "message": "No data to export"
                }
            
            # Get headers from first row
            headers = list(data[0].keys())
            
            # Prepare values
            values = [headers]
            for row in data:
                values.append([str(row.get(header, '')) for header in headers])
            
            # Clear existing data
            try:
                self.service.spreadsheets().values().clear(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A:Z"
                ).execute()
            except HttpError:
                # Sheet might not exist, create it
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': requests}
                ).execute()
            
            # Update with new data
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption='RAW',
                body={'values': values}
            ).execute()
            
            return {
                "spreadsheet_id": spreadsheet_id,
                "sheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
                "message": f"Exported {len(data)} records successfully"
            }
            
        except HttpError as error:
            raise Exception(f"Google Sheets API error: {error}")
    
    async def import_data(
        self, 
        spreadsheet_id: str, 
        sheet_name: str = "Shifts Data",
        range_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Import data from Google Sheets"""
        if not self.service:
            raise Exception("Google Sheets service not initialized. Please configure credentials.")
        
        try:
            # Determine range
            if not range_name:
                range_name = f"{sheet_name}!A:Z"
            
            # Get data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            # First row as headers
            headers = values[0]
            data = []
            
            # Process remaining rows
            for row in values[1:]:
                # Pad row with empty strings if shorter than headers
                while len(row) < len(headers):
                    row.append('')
                
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ''
                
                data.append(row_dict)
            
            return data
            
        except HttpError as error:
            raise Exception(f"Google Sheets API error: {error}")
    
    def is_available(self) -> bool:
        """Check if Google Sheets service is available"""
        return self.service is not None 