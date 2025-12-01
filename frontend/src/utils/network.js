/**
 * Network utility functions for determining API and WebSocket URLs.
 * Handles remote access detection when running in Vite development mode.
 */

const LOCALHOST_HOSTS = ['localhost', '127.0.0.1', '::1'];
const DEFAULT_BACKEND_PORT = '8000';

/**
 * Check if the current hostname is a localhost address.
 * @returns {boolean}
 */
export const isLocalhost = () => {
  return LOCALHOST_HOSTS.includes(window.location.hostname);
};

/**
 * Check if running in remote access dev mode (dev mode accessed from non-localhost).
 * @returns {boolean}
 */
export const isRemoteDevAccess = () => {
  return import.meta.env.DEV && !isLocalhost();
};

/**
 * Check if VITE_API_URL and VITE_WS_URL are configured.
 * @returns {boolean}
 */
export const hasExplicitConfig = () => {
  return Boolean(import.meta.env.VITE_API_URL && import.meta.env.VITE_WS_URL);
};

/**
 * Get the API URL based on the current environment.
 * 
 * Priority:
 * 1. VITE_API_URL environment variable if set
 * 2. Production mode: use window.location.protocol + host
 * 3. Dev mode with remote access: use window.location.hostname + port 8000
 * 4. Default: http://localhost:8000
 * 
 * @returns {string} The API URL
 */
export const getApiUrl = () => {
  // 1. Check for explicit environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // 2. Production mode: use current host (nginx proxies to backend)
  if (import.meta.env.PROD) {
    return `${window.location.protocol}//${window.location.host}`;
  }

  // 3. Dev mode with non-localhost access: construct URL using server's hostname
  if (import.meta.env.DEV && !isLocalhost()) {
    const url = `${window.location.protocol}//${window.location.hostname}:${DEFAULT_BACKEND_PORT}`;
    console.warn(
      `[Network] Dev mode accessed remotely from ${window.location.hostname}. ` +
      `Using auto-detected API URL: ${url}. ` +
      `To configure explicitly, set VITE_API_URL in .env file.`
    );
    return url;
  }

  // 4. Default for local development
  return `http://localhost:${DEFAULT_BACKEND_PORT}`;
};

/**
 * Get the WebSocket URL based on the current environment.
 * 
 * Priority:
 * 1. VITE_WS_URL environment variable if set
 * 2. Production mode: use ws/wss based on protocol + host
 * 3. Dev mode with remote access: use window.location.hostname + port 8000
 * 4. Default: ws://localhost:8000
 * 
 * @returns {string} The WebSocket URL
 */
export const getWsUrl = () => {
  // 1. Check for explicit environment variable
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }

  // 2. Production mode: construct WebSocket URL using current host
  if (import.meta.env.PROD) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}`;
  }

  // 3. Dev mode with non-localhost access: construct URL using server's hostname
  if (import.meta.env.DEV && !isLocalhost()) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.hostname}:${DEFAULT_BACKEND_PORT}`;
    console.warn(
      `[Network] Dev mode accessed remotely from ${window.location.hostname}. ` +
      `Using auto-detected WebSocket URL: ${url}. ` +
      `To configure explicitly, set VITE_WS_URL in .env file.`
    );
    return url;
  }

  // 4. Default for local development
  return `ws://localhost:${DEFAULT_BACKEND_PORT}`;
};
