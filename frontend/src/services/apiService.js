import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

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
  // Raw HTTP methods
  get: (url, config = {}) => apiClient.get(url, config),
  post: (url, data = {}, config = {}) => apiClient.post(url, data, config),
  put: (url, data = {}, config = {}) => apiClient.put(url, data, config),
  delete: (url, config = {}) => apiClient.delete(url, config),
  
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

  // Teachers 
  async getTeachers(schoolId) {
    const response = await apiClient.get(`/teachers/${schoolId}/`);
    return response.data;
  },

  async addTeacher(schoolId, teacherData) {
    const response = await apiClient.post(`/teachers/${schoolId}/add/`, teacherData);
    return response.data;
  },

  async updateTeacher(schoolId, teacherId, teacherData) {
    const response = await apiClient.put(`/teachers/${schoolId}/${teacherId}/update/`, teacherData);
    return response.data;
  },

  async deleteTeacher(schoolId, teacherId) {
    const response = await apiClient.delete(`/teachers/${schoolId}/${teacherId}/delete/`);
    return response.data;
  },

  // Arrangements
  async getAbsentTeachers(schoolId, date = null) {
    let url = `/arrangements/${schoolId}/absent-teachers/`;
    if (date) url += `?date=${date}`;
    const response = await apiClient.get(url);
    return response.data;
  },

  async getArrangements(schoolId, date = null) {
    let url = `/arrangements/${schoolId}/arrangements/`;
    if (date) url += `?date=${date}`;
    const response = await apiClient.get(url);
    return response.data;
  },

  async createManualArrangement(schoolId, arrangementData) {
    const response = await apiClient.post(`/arrangements/${schoolId}/create-manual/`, arrangementData);
    return response.data;
  },

  // Attendance
  async getAttendanceReport(schoolId, startDate, endDate) {
    const response = await apiClient.get(`/attendance/${schoolId}/report/?start_date=${startDate}&end_date=${endDate}`);
    return response.data;
  },

  async markAttendance(schoolId, attendanceData) {
    const response = await apiClient.post(`/attendance/${schoolId}/mark/`, attendanceData);
    return response.data;
  },

  async getDailyAttendance(schoolId, date = null) {
    let url = `/attendance/${schoolId}/daily/`;
    if (date) url += `?date=${date}`;
    const response = await apiClient.get(url);
    return response.data;
  },

  // Schedules
  async getSchoolSchedule(schoolId) {
    const response = await apiClient.get(`/schedules/${schoolId}/`);
    return response.data;
  },

  async getTeacherSchedule(schoolId, teacherId) {
    const response = await apiClient.get(`/schedules/${schoolId}/teacher/${teacherId}/`);
    return response.data;
  },
};