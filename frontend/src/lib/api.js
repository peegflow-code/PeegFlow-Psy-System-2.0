import axios from "axios";
import { getToken, clearToken } from "./auth";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getTenantSlug() {
  try {
    return localStorage.getItem("tenant_slug") || "";
  } catch {
    return "";
  }
}

export const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;

  // ✅ Multi-tenant: envia o slug em TODAS as requests
  const slug = getTenantSlug();
  if (slug) config.headers["X-Tenant-Slug"] = slug;

  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401) {
      clearToken();
    }
    return Promise.reject(err);
  }
);