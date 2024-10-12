// src/axiosInstance.js
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000', // Base URL for all requests
  headers: {
    'Content-Type': 'application/json',
    // You can set additional headers like Authorization here if needed
  },
});

// Optionally add request/response interceptors
axiosInstance.interceptors.request.use(
  (config) => {
    // Modify request config if needed (e.g., add authorization token)
    const auth = JSON.parse(localStorage.getItem('auth'));
    if (auth?.token?.access) {
      config.headers['Authorization'] = `Bearer ${auth?.token?.access}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle error (e.g., log out user on 401 Unauthorized, etc.)
    return Promise.reject(error);
  }
);

export default axiosInstance;
