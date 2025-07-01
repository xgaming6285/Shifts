import React, { useState, useEffect } from 'react';
import { 
  UsersIcon, 
  ClockIcon, 
  CalendarDaysIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline';
import { api } from '../services/api';

interface DashboardStats {
  total_workers: number;
  active_workers: number;
  total_shifts_today: number;
  workers_clocked_in: number;
  total_hours_today: number;
  overtime_hours_today: number;
}

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
  total_hours: number;
  status: string;
  worker: Worker;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    total_workers: 0,
    active_workers: 0,
    total_shifts_today: 0,
    workers_clocked_in: 0,
    total_hours_today: 0,
    overtime_hours_today: 0,
  });
  const [activeRecords, setActiveRecords] = useState<TimeRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, activeRecordsResponse] = await Promise.all([
        api.get('/tracking/dashboard'),
        api.get('/tracking/active')
      ]);
      
      setStats(statsResponse.data);
      setActiveRecords(activeRecordsResponse.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      name: 'Total Workers',
      value: stats.total_workers,
      icon: UsersIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Workers',
      value: stats.active_workers,
      icon: UsersIcon,
      color: 'bg-green-500',
    },
    {
      name: "Today's Shifts",
      value: stats.total_shifts_today,
      icon: CalendarDaysIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'Currently Clocked In',
      value: stats.workers_clocked_in,
      icon: ClockIcon,
      color: 'bg-orange-500',
    },
  ];

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
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your workforce and shifts
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((item) => (
          <div
            key={item.name}
            className="relative bg-white pt-5 px-4 pb-12 sm:pt-6 sm:px-6 shadow rounded-lg overflow-hidden"
          >
            <dt>
              <div className={`absolute ${item.color} rounded-md p-3`}>
                <item.icon className="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              <p className="ml-16 text-sm font-medium text-gray-500 truncate">
                {item.name}
              </p>
            </dt>
            <dd className="ml-16 pb-6 flex items-baseline sm:pb-7">
              <p className="text-2xl font-semibold text-gray-900">
                {item.value}
              </p>
            </dd>
          </div>
        ))}
      </div>

      {/* Hours Summary */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Today's Hours</h3>
          <ChartBarIcon className="h-5 w-5 text-gray-400" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">
              {stats.total_hours_today.toFixed(1)}
            </p>
            <p className="text-sm text-blue-600">Total Hours</p>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <p className="text-2xl font-bold text-orange-600">
              {stats.overtime_hours_today.toFixed(1)}
            </p>
            <p className="text-sm text-orange-600">Overtime Hours</p>
          </div>
        </div>
      </div>

      {/* Currently Active Workers */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Currently Clocked In
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
                      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">
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
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-900">
                      Clocked in at{' '}
                      {new Date(record.clock_in).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                    <div className="text-sm text-gray-500">
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
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <button className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            Add New Worker
          </button>
          <button className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
            Schedule Shift
          </button>
          <button className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500">
            Export Data
          </button>
        </div>
      </div>
    </div>
  );
} 