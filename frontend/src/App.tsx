import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Workers from './components/Workers';
import Shifts from './components/Shifts';
import TimeTracking from './components/TimeTracking';
import Reports from './components/Reports';
import Settings from './components/Settings';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
        
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <button
                    type="button"
                    className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                    onClick={() => setSidebarOpen(true)}
                  >
                    <span className="sr-only">Open sidebar</span>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                  </button>
                  <h1 className="ml-4 text-2xl font-bold text-gray-900">
                    Work Shifts Tracker
                  </h1>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-500">
                    {new Date().toLocaleDateString('en-US', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </span>
                </div>
              </div>
            </div>
          </header>

          <main className="flex-1 overflow-y-auto">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/workers" element={<Workers />} />
                <Route path="/shifts" element={<Shifts />} />
                <Route path="/tracking" element={<TimeTracking />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
