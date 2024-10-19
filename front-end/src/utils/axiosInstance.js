import axios from "axios";
import { store } from '../redux/store';  

const axiosInstance = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const { auth } = store?.getState()?.auth;

    if (auth?.token?.access) {
      config.headers["Authorization"] = `Bearer ${auth?.token?.access}`;
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
