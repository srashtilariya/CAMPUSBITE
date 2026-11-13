import axios from 'axios';
import { clearSession, readToken } from '../state/storage';

export const SESSION_EXPIRED_EVENT = 'cb:session-expired';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 45_000,
});

http.interceptors.request.use((config) => {
  const token = readToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const unauthorised = error.response?.status === 401;
    if (unauthorised && readToken()) {
      clearSession();
      window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
    }
    return Promise.reject(error);
  },
);

/** Strip blank query values so the API never receives `?status=` style params. */
export function withoutBlanks(query = {}) {
  const result = {};
  for (const [key, value] of Object.entries(query)) {
    if (value === '' || value === null || value === undefined) continue;
    result[key] = value;
  }
  return result;
}

/** Shorthand helpers that resolve straight to the response body. */
export const get = (url, params) => http.get(url, { params }).then((res) => res.data);
export const post = (url, body) => http.post(url, body).then((res) => res.data);
export const put = (url, body) => http.put(url, body).then((res) => res.data);
export const patch = (url, body) => http.patch(url, body).then((res) => res.data);
export const remove = (url) => http.delete(url).then((res) => res.data);

/** Turn an axios / FastAPI error into a sentence a person can read. */
export function describeError(error, fallback = 'Something didn’t work. Please try again.') {
  if (!error) return fallback;
  const detail = error.response?.data?.detail;

  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map(({ loc, msg }) => {
        const field = Array.isArray(loc) ? loc[loc.length - 1] : '';
        return field ? `${field}: ${msg}` : msg;
      })
      .join(' · ');
  }
  if (error.code === 'ECONNABORTED') return 'The server took too long to answer.';
  if (error.message === 'Network Error') return 'Can’t reach the CampusBite server right now.';
  return fallback;
}

export default http;
