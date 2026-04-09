import axios from "axios";
import { authStore } from "@/store/auth";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

api.interceptors.request.use((config) => {
  if (authStore.state.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.state.accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStore.clear();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

export default api;

export const messageApi = {
  list(params = {}) {
    return api.get("/messages", { params });
  },
  clear() {
    return api.post("/messages/clear");
  },
};
