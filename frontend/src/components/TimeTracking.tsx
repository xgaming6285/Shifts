import React, { useState, useEffect } from 'react';
import { ClockIcon, PlayIcon, StopIcon } from '@heroicons/react/24/outline';
import { trackingApi, workerApi } from '../services/api';

interface Worker {
  id: number;
  name: string;
  email: string;
  position: string;
  is_active: boolean;
}

interface TimeRecord {
  id: number;
  worker_id: number;
  clock_in: string;
  clock_out: string | null;
  break_start: string | null;
  break_end: string | null;
  total_hours: number;
  status: string;
  worker: Worker;
}

export default function TimeTracking() {
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [activeRecords, setActiveRecords] = useState<TimeRecord[]>([]);
  const [selectedWorker, setSelectedWorker] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [workersResponse, activeRecordsResponse] = await Promise.all([
        workerApi.getAll(),
        trackingApi.getActive()
      ]);
      setWorkers(workersResponse.data.filter((w: Worker) => w.is_active));
      setActiveRecords(activeRecordsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClockIn = async () => {
    if (!selectedWorker) return;
    
    try {
      await trackingApi.clockIn({ worker_id: selectedWorker });
      await fetchData();
      setSelectedWorker(null);
    } catch (error) {
      console.error('Error clocking in:', error);
    }
  };

  const handleClockOut = async (recordId: number) => {
    try {
      await trackingApi.clockOut(recordId);
      await fetchData();
    } catch (error) {
      console.error('Error clocking out:', error);
    }
  };

  const handleBreakStart = async (recordId: number) => {
    try {
      await trackingApi.startBreak(recordId);
      await fetchData();
    } catch (error) {
      console.error('Error starting break:', error);
    }
  };

  const handleBreakEnd = async (recordId: number) => {
    try {
      await trackingApi.endBreak(recordId);
      await fetchData();
    } catch (error) {
      console.error('Error ending break:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Time Tracking</h1>
        <p className="mt-1 text-sm text-gray-500">
          Clock in/out and manage work time
        </p>
      </div>

      {/* Clock In Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Clock In</h3>
        <div className="flex items-center space-x-4">
          <select
            value={selectedWorker || ''}
            onChange={(e) => setSelectedWorker(Number(e.target.value) || null)}
            className="block w-64 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select a worker...</option>
            {workers
              .filter(worker => !activeRecords.some(record => record.worker_id === worker.id))
              .map((worker) => (
                <option key={worker.id} value={worker.id}>
                  {worker.name} - {worker.position}
                </option>
              ))}
          </select>
          <button
            onClick={handleClockIn}
            disabled={!selectedWorker}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            Clock In
          </button>
        </div>
      </div>

      {/* Active Workers */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Currently Clocked In ({activeRecords.length})
          </h3>
        </div>
        <div className="divide-y divide-gray-200">
          {activeRecords.length === 0 ? (
            <div className="px-6 py-8 text-center">
              <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No workers clocked in
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                All workers are currently clocked out.
              </p>
            </div>
          ) : (
            activeRecords.map((record) => (
              <div key={record.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                        <span className="text-sm font-medium text-green-600">
                          {record.worker.name.charAt(0)}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {record.worker.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {record.worker.position}
                      </div>
                      <div className="text-xs text-gray-400">
                        Started: {new Date(record.clock_in).toLocaleTimeString()}
                        {record.break_start && !record.break_end && (
                          <span className="ml-2 text-orange-600">On Break</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="text-right mr-4">
                      <div className="text-sm font-medium text-gray-900">
                        {Math.floor(
                          (Date.now() - new Date(record.clock_in).getTime()) /
                            (1000 * 60 * 60)
                        )}h{' '}
                        {Math.floor(
                          ((Date.now() - new Date(record.clock_in).getTime()) %
                            (1000 * 60 * 60)) /
                            (1000 * 60)
                        )}m
                      </div>
                      <div className="text-xs text-gray-500">Total Time</div>
                    </div>
                    {record.break_start && !record.break_end ? (
                      <button
                        onClick={() => handleBreakEnd(record.id)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-orange-700 bg-orange-100 hover:bg-orange-200"
                      >
                        End Break
                      </button>
                    ) : (
                      <button
                        onClick={() => handleBreakStart(record.id)}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-yellow-700 bg-yellow-100 hover:bg-yellow-200"
                      >
                        Start Break
                      </button>
                    )}
                    <button
                      onClick={() => handleClockOut(record.id)}
                      className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-white bg-red-600 hover:bg-red-700"
                    >
                      <StopIcon className="h-3 w-3 mr-1" />
                      Clock Out
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
} 