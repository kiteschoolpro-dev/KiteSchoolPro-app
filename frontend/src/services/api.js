import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Course API
export const courseApi = {
  getAll: async () => {
    const response = await axios.get(`${API}/courses/`);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await axios.get(`${API}/courses/${id}`);
    return response.data;
  },
  
  getByType: async (type) => {
    const response = await axios.get(`${API}/courses/by-type/${type}`);
    return response.data;
  },
  
  getBySpot: async (spot) => {
    const response = await axios.get(`${API}/courses/by-spot/${spot}`);
    return response.data;
  }
};

// Booking API
export const bookingApi = {
  checkAvailability: async (availabilityData) => {
    const response = await axios.post(`${API}/bookings/check-availability`, availabilityData);
    return response.data;
  },
  
  create: async (bookingData) => {
    const response = await axios.post(`${API}/bookings/`, bookingData);
    return response.data;
  },
  
  getMyBookings: async () => {
    const response = await axios.get(`${API}/bookings/my-bookings`);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await axios.get(`${API}/bookings/${id}`);
    return response.data;
  },
  
  updateStatus: async (id, status) => {
    const response = await axios.patch(`${API}/bookings/${id}/status?status=${status}`);
    return response.data;
  }
};

// Payment API
export const paymentApi = {
  createPaymentIntent: async (paymentData) => {
    const response = await axios.post(`${API}/payments/create-payment-intent`, paymentData);
    return response.data;
  },
  
  confirmPayment: async (paymentId) => {
    const response = await axios.post(`${API}/payments/confirm-payment/${paymentId}`);
    return response.data;
  },
  
  getBookingPayments: async (bookingId) => {
    const response = await axios.get(`${API}/payments/booking/${bookingId}`);
    return response.data;
  }
};

// Admin API
export const adminApi = {
  getDashboardStats: async () => {
    const response = await axios.get(`${API}/admin/dashboard`);
    return response.data;
  },
  
  getUsers: async () => {
    const response = await axios.get(`${API}/admin/users`);
    return response.data;
  },
  
  getInstructors: async () => {
    const response = await axios.get(`${API}/admin/instructors`);
    return response.data;
  },
  
  createInstructorSchedule: async (scheduleData) => {
    const response = await axios.post(`${API}/admin/instructor-schedule`, scheduleData);
    return response.data;
  },
  
  getInstructorSchedules: async (instructorId, startDate, endDate) => {
    const response = await axios.get(`${API}/admin/instructor-schedules/${instructorId}?start_date=${startDate}&end_date=${endDate}`);
    return response.data;
  },
  
  getTodayBookings: async () => {
    const response = await axios.get(`${API}/admin/bookings/today`);
    return response.data;
  },
  
  updateUserRole: async (userId, role) => {
    const response = await axios.patch(`${API}/admin/users/${userId}/role?new_role=${role}`);
    return response.data;
  }
};