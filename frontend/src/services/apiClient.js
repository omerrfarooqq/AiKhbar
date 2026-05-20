import axios from 'axios';

// Base URL is empty in dev (Vite proxies /api); set VITE_API_BASE_URL in prod.
const baseURL = import.meta.env.VITE_API_BASE_URL || '';

export const apiClient = axios.create({
  baseURL: `${baseURL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000, // AI endpoints (briefs, summaries) can be slow.
});

// Surface a clean error message to callers / UI.
apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    const detail =
      error.response?.data?.detail || error.message || 'Request failed';
    return Promise.reject(new Error(detail));
  },
);
