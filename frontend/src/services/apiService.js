import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth headers if needed
apiClient.interceptors.request.use(
  (config) => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.token) {
      config.headers.Authorization = `Bearer ${user.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Authentication
  async getSchools() {
    const response = await apiClient.get('/auth/schools/');
    return response.data;
  },

  async login(credentials) {
    const response = await apiClient.post('/auth/login/', credentials);
    return response.data;
  },

  async logout() {
    const response = await apiClient.post('/auth/logout/');
    return response.data;
  },

  async getProfile() {
    const response = await apiClient.get('/auth/profile/');
    return response.data;
  },

  // Teachers
  async getTeachers(schoolId) {
    const response = await apiClient.get(`/teachers/?school_id=${schoolId}`);
    return response.data;
  },

  async addTeacher(teacherData) {
    const response = await apiClient.post('/teachers/add/', teacherData);
    return response.data;
  },

  async updateTeacher(teacherId, teacherData) {
    const response = await apiClient.put(`/teachers/${teacherId}/update/`, teacherData);
    return response.data;
  },

  async deleteTeacher(teacherId) {
    const response = await apiClient.delete(`/teachers/${teacherId}/delete/`);
    return response.data;
  },

  async getSchedule(schoolId, dayOfWeek = null) {
    let url = `/teachers/schedule/?school_id=${schoolId}`;
    if (dayOfWeek) {
      url += `&day_of_week=${dayOfWeek}`;
    }
    const response = await apiClient.get(url);
    return response.data;
  },

  async getWorkload(schoolId) {
    const response = await apiClient.get(`/teachers/workload/?school_id=${schoolId}`);
    return response.data;
  },

  async getSubstitutes(schoolId) {
    const response = await apiClient.get(`/teachers/substitutes/?school_id=${schoolId}`);
    return response.data;
  },

  // Arrangements (to be implemented)
  async getArrangements(schoolId) {
    // Placeholder - implement when backend is ready
    return { success: true, arrangements: [] };
  },

  // Attendance (to be implemented)
  async getAttendance(schoolId) {
    // Placeholder - implement when backend is ready
    return { success: true, attendance: [] };
  },
};