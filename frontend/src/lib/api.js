import axios from "axios";
import { getToken, clearToken } from "./auth";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const status = err?.response?.status;
    const url = err?.config?.url || "";

    // evita limpar token por erro de login ou rotas públicas
    if (status === 401 && !url.includes("/auth/login")) {
      clearToken();
    }

    return Promise.reject(err);
  }
);