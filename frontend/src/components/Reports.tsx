import React, { useState } from 'react';
import { DocumentArrowDownIcon, DocumentArrowUpIcon } from '@heroicons/react/24/outline';
import { googleSheetsApi } from '../services/api';

export default function Reports() {
  const [loading, setLoading] = useState(false);
  const [exportData, setExportData] = useState({
    spreadsheet_id: '',
    sheet_name: 'Shifts Data',
  });

  const handleExportToSheets = async () => {
    setLoading(true);
    try {
      const response = await googleSheetsApi.export(exportData);
      alert(`Data exported successfully! ${response.data.records_exported} records exported.`);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please check your Google Sheets configuration.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportToCsv = async () => {
    setLoading(true);
    try {
      const response = await googleSheetsApi.exportCsv();
      const blob = new Blob([response.data.csv_data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.data.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('CSV export failed:', error);
      alert('CSV export failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    try {
      const response = await googleSheetsApi.uploadCsv(file);
      alert(`Import completed! ${response.data.imported_count} records imported.`);
    } catch (error) {
      console.error('Import failed:', error);
      alert('Import failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports & Export</h1>
        <p className="mt-1 text-sm text-gray-500">
          Export data to Google Sheets or CSV, and import data
        </p>
      </div>

      {/* Export Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Export Data</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Google Sheets Export */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="text-md font-medium text-gray-900 mb-3">
              Export to Google Sheets
            </h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Spreadsheet ID (optional)
                </label>
                <input
                  type="text"
                  value={exportData.spreadsheet_id}
                  onChange={(e) =>
                    setExportData({ ...exportData, spreadsheet_id: e.target.value })
                  }
                  placeholder="Leave empty to create new spreadsheet"
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Sheet Name
                </label>
                <input
                  type="text"
                  value={exportData.sheet_name}
                  onChange={(e) =>
                    setExportData({ ...exportData, sheet_name: e.target.value })
                  }
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <button
                onClick={handleExportToSheets}
                disabled={loading}
                className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-400"
              >
                <DocumentArrowUpIcon className="h-4 w-4 mr-2" />
                {loading ? 'Exporting...' : 'Export to Google Sheets'}
              </button>
            </div>
          </div>

          {/* CSV Export */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="text-md font-medium text-gray-900 mb-3">
              Export to CSV
            </h4>
            <p className="text-sm text-gray-500 mb-4">
              Download all time tracking data as a CSV file
            </p>
            <button
              onClick={handleExportToCsv}
              disabled={loading}
              className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
            >
              <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              {loading ? 'Exporting...' : 'Download CSV'}
            </button>
          </div>
        </div>
      </div>

      {/* Import Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Import Data</h3>
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="text-md font-medium text-gray-900 mb-3">
            Import from CSV
          </h4>
          <p className="text-sm text-gray-500 mb-4">
            Upload a CSV file with worker data. Required columns: Worker Name, Worker Email
          </p>
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <DocumentArrowUpIcon className="w-8 h-8 mb-4 text-gray-500" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">CSV files only</p>
              </div>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
                disabled={loading}
              />
            </label>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Export Options</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-600 font-medium">Current Week</p>
            <p className="text-xs text-blue-500">Export this week's data</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-green-600 font-medium">Current Month</p>
            <p className="text-xs text-green-500">Export this month's data</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-sm text-purple-600 font-medium">All Data</p>
            <p className="text-xs text-purple-500">Export all historical data</p>
          </div>
        </div>
      </div>
    </div>
  );
} 