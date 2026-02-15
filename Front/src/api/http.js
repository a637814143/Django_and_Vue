import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api/";

const http = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 15000,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("sessionToken");
  if (token) {
    config.headers["X-SESSION-TOKEN"] = token;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 302) {
      const redirect = encodeURIComponent(window.location.pathname);
      window.location.href = `/login?redirect=${redirect}`;
    }
    return Promise.reject(error);
  },
);

export default http;
