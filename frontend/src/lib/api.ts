/**
 * =============================================================================
 * API Client — Axios Instance
 * =============================================================================
 * Pre-configured Axios instance for all API calls to the BFF.
 *
 * withCredentials: true  → sends httpOnly cookies on every request.
 * Without this, the browser won't attach the access_token cookie
 * to cross-origin requests (localhost:3000 → localhost:8000).
 * =============================================================================
 */
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true,     // CRITICAL: sends cookies on every request
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
