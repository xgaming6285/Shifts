import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token (if needed in future)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      // Redirect to login if needed
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const workerApi = {
  getAll: () => api.get('/workers'),
  getById: (id: number) => api.get(`/workers/${id}`),
  create: (data: any) => api.post('/workers', data),
  update: (id: number, data: any) => api.put(`/workers/${id}`, data),
  delete: (id: number) => api.delete(`/workers/${id}`),
  getStats: (id: number) => api.get(`/workers/${id}/stats`),
};

export const shiftApi = {
  getAll: (params?: any) => api.get('/shifts', { params }),
  getById: (id: number) => api.get(`/shifts/${id}`),
  create: (data: any) => api.post('/shifts', data),
  update: (id: number, data: any) => api.put(`/shifts/${id}`, data),
  delete: (id: number) => api.delete(`/shifts/${id}`),
  getToday: () => api.get('/shifts/today'),
  getUpcoming: (workerId: number) => api.get(`/shifts/worker/${workerId}/upcoming`),
};

export const trackingApi = {
  clockIn: (data: any) => api.post('/tracking/clock-in', data),
  clockOut: (recordId: number) => api.put(`/tracking/clock-out/${recordId}`),
  startBreak: (recordId: number) => api.put(`/tracking/break-start/${recordId}`),
  endBreak: (recordId: number) => api.put(`/tracking/break-end/${recordId}`),
  getActive: () => api.get('/tracking/active'),
  getWorkerActive: (workerId: number) => api.get(`/tracking/worker/${workerId}/active`),
  getRecords: (params?: any) => api.get('/tracking/records', { params }),
  getDashboard: () => api.get('/tracking/dashboard'),
};

export const googleSheetsApi = {
  export: (data: any) => api.post('/google-sheets/export', data),
  import: (data: any) => api.post('/google-sheets/import', data),
  uploadCsv: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/google-sheets/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  exportCsv: (params?: any) => api.get('/google-sheets/export-csv', { params }),
}; 