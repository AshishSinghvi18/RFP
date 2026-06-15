import axios, { AxiosError, type AxiosRequestConfig } from 'axios';

import type { ApiEnvelope } from '@/utils/types';

export const TOKEN_STORAGE_KEY = 'rfp-intelligence.token';
export const USER_STORAGE_KEY = 'rfp-intelligence.user';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = 'Bearer ' + token;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_STORAGE_KEY);

      if (window.location.pathname !== '/login') {
        window.location.assign('/login');
      }
    }

    return Promise.reject(error);
  },
);

export const unwrap = <T>(payload: T | ApiEnvelope<T>): T => {
  if (typeof payload === 'object' && payload !== null && 'data' in payload && 'success' in payload) {
    return payload.data;
  }

  return payload as T;
};

export const getApiErrorMessage = (error: unknown, fallback = 'Something went wrong.') => {
  if (error instanceof AxiosError) {
    return (error.response?.data as { detail?: string } | undefined)?.detail ?? error.message ?? fallback;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
};

export const get = async <T>(url: string, config?: AxiosRequestConfig) => {
  const response = await api.get<T | ApiEnvelope<T>>(url, config);
  return unwrap<T>(response.data);
};

export const post = async <T>(url: string, data?: unknown, config?: AxiosRequestConfig) => {
  const response = await api.post<T | ApiEnvelope<T>>(url, data, config);
  return unwrap<T>(response.data);
};

export const patch = async <T>(url: string, data?: unknown, config?: AxiosRequestConfig) => {
  const response = await api.patch<T | ApiEnvelope<T>>(url, data, config);
  return unwrap<T>(response.data);
};

export default api;
