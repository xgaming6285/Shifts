# Work Shifts Tracker

A comprehensive work shifts tracking system built with Python FastAPI backend and React TypeScript frontend.

## Features

### Core Functionality
- **Worker Management**: Add, edit, and manage worker information
- **Shift Scheduling**: Create and manage work shifts
- **Time Tracking**: Clock in/out functionality with break tracking
- **Dashboard**: Real-time overview of workforce status
- **Reports & Export**: Export data to Google Sheets and CSV

### Key Features
- ⏰ Real-time time tracking with automatic calculations
- 📊 Dashboard with workforce statistics
- 📅 Shift scheduling and management
- 👥 Complete worker profile management
- 📈 Overtime tracking and reporting
- 🔄 Google Sheets integration for import/export
- 📱 Responsive design with modern UI
- 🎨 Built with Tailwind CSS and Heroicons

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **SQLite**: Default database (PostgreSQL supported)
- **Google Sheets API**: For data import/export
- **Pandas**: Data manipulation and analysis

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Heroicons**: Beautiful hand-crafted SVG icons
- **Headless UI**: Unstyled, accessible UI components
- **Axios**: HTTP client for API requests
- **React Router**: Client-side routing

## Installation & Setup

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   ```bash
   cp env.example .env
   # Edit .env file with your configuration
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./shifts_tracker.db

# Google Sheets Integration (Optional)
GOOGLE_CREDENTIALS_PATH=/path/to/your/service-account-key.json
# OR
GOOGLE_CREDENTIALS_JSON={"type": "service_account", "project_id": "your-project", ...}

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Google Sheets Integration

To enable Google Sheets integration:

1. Create a Google Cloud Project
2. Enable the Google Sheets API
3. Create a service account and download the JSON key
4. Set the `GOOGLE_CREDENTIALS_PATH` or `GOOGLE_CREDENTIALS_JSON` environment variable

## API Endpoints

### Workers
- `GET /api/workers` - Get all workers
- `POST /api/workers` - Create new worker
- `GET /api/workers/{id}` - Get worker by ID
- `PUT /api/workers/{id}` - Update worker
- `DELETE /api/workers/{id}` - Deactivate worker

### Shifts
- `GET /api/shifts` - Get all shifts
- `POST /api/shifts` - Create new shift
- `GET /api/shifts/today` - Get today's shifts
- `GET /api/shifts/worker/{id}/upcoming` - Get upcoming shifts for worker

### Time Tracking
- `POST /api/tracking/clock-in` - Clock in worker
- `PUT /api/tracking/clock-out/{id}` - Clock out worker
- `PUT /api/tracking/break-start/{id}` - Start break
- `PUT /api/tracking/break-end/{id}` - End break
- `GET /api/tracking/active` - Get active time records
- `GET /api/tracking/dashboard` - Get dashboard statistics

### Google Sheets
- `POST /api/google-sheets/export` - Export to Google Sheets
- `POST /api/google-sheets/import` - Import from Google Sheets
- `POST /api/google-sheets/upload-csv` - Upload CSV file
- `GET /api/google-sheets/export-csv` - Export to CSV

## Usage

### Adding Workers
1. Navigate to the Workers page
2. Click "Add Worker"
3. Fill in worker information
4. Save to create the worker profile

### Time Tracking
1. Go to Time Tracking page
2. Select a worker from the dropdown
3. Click "Clock In" to start tracking
4. Use break controls as needed
5. Click "Clock Out" to end the session

### Shift Management
1. Access the Shifts page
2. Create new shifts by specifying worker, date, and time
3. View and manage existing shifts
4. Track shift completion status

### Data Export
1. Visit the Reports page
2. Choose export format (Google Sheets or CSV)
3. Configure export settings
4. Download or share the exported data

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm run build
```

## Database Schema

### Workers Table
- `id`: Primary key
- `name`: Worker name
- `email`: Email address (unique)
- `phone`: Phone number
- `position`: Job position
- `hourly_rate`: Hourly wage rate
- `is_active`: Active status
- `created_at`: Creation timestamp

### Shifts Table
- `id`: Primary key
- `worker_id`: Foreign key to workers
- `date`: Shift date
- `start_time`: Shift start time
- `end_time`: Shift end time
- `status`: Shift status (scheduled, completed, cancelled)
- `notes`: Additional notes

### Time Records Table
- `id`: Primary key
- `worker_id`: Foreign key to workers
- `shift_id`: Foreign key to shifts (optional)
- `clock_in`: Clock in timestamp
- `clock_out`: Clock out timestamp
- `break_start`: Break start timestamp
- `break_end`: Break end timestamp
- `total_hours`: Total hours worked
- `overtime_hours`: Overtime hours
- `status`: Record status (active, completed)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue on the GitHub repository. 