import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Helper to mock import.meta.env and window.location
const mockEnvAndLocation = (env, location) => {
  // Mock import.meta.env values on the module
  vi.stubGlobal('location', {
    hostname: location.hostname || 'localhost',
    protocol: location.protocol || 'http:',
    host: location.host || 'localhost:5173',
  });

  return env;
};

describe('network utilities', () => {
  let originalLocation;
  let consoleWarnSpy;

  beforeEach(() => {
    // Save original window.location
    originalLocation = window.location;
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    // Reset modules before each test to get fresh import.meta.env reads
    vi.resetModules();
  });

  afterEach(() => {
    // Restore original window.location
    vi.stubGlobal('location', originalLocation);
    consoleWarnSpy.mockRestore();
    vi.unstubAllGlobals();
  });

  describe('getApiUrl', () => {
    it('should return VITE_API_URL when set', async () => {
      vi.stubGlobal('location', {
        hostname: 'localhost',
        protocol: 'http:',
        host: 'localhost:5173',
      });

      // Dynamically import the module with mocked env
      vi.stubEnv('VITE_API_URL', 'http://custom-api.example.com:3000');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getApiUrl } = await import('./network.js');
      expect(getApiUrl()).toBe('http://custom-api.example.com:3000');
    });

    it('should use window.location.host in production mode', async () => {
      vi.stubGlobal('location', {
        hostname: '192.168.1.100',
        protocol: 'https:',
        host: '192.168.1.100',
      });

      vi.stubEnv('VITE_API_URL', '');
      vi.stubEnv('DEV', false);
      vi.stubEnv('PROD', true);

      const { getApiUrl } = await import('./network.js');
      expect(getApiUrl()).toBe('https://192.168.1.100');
    });

    it('should fallback to localhost:8000 in dev mode when accessing from localhost', async () => {
      vi.stubGlobal('location', {
        hostname: 'localhost',
        protocol: 'http:',
        host: 'localhost:5173',
      });

      vi.stubEnv('VITE_API_URL', '');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getApiUrl } = await import('./network.js');
      expect(getApiUrl()).toBe('http://localhost:8000');
    });

    it('should use window.location.hostname:8000 in dev mode when accessed remotely', async () => {
      vi.stubGlobal('location', {
        hostname: '192.168.1.50',
        protocol: 'http:',
        host: '192.168.1.50:5173',
      });

      vi.stubEnv('VITE_API_URL', '');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getApiUrl } = await import('./network.js');
      expect(getApiUrl()).toBe('http://192.168.1.50:8000');
      expect(consoleWarnSpy).toHaveBeenCalled();
    });

    it('should fallback to localhost:8000 in dev mode when hostname is 127.0.0.1', async () => {
      vi.stubGlobal('location', {
        hostname: '127.0.0.1',
        protocol: 'http:',
        host: '127.0.0.1:5173',
      });

      vi.stubEnv('VITE_API_URL', '');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getApiUrl } = await import('./network.js');
      expect(getApiUrl()).toBe('http://localhost:8000');
    });

    it('should fallback to localhost:8000 in dev mode when hostname is ::1', async () => {
      vi.stubGlobal('location', {
        hostname: '::1',
        protocol: 'http:',
        host: '[::1]:5173',
      });

      vi.stubEnv('VITE_API_URL', '');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getApiUrl } = await import('./network.js');
      expect(getApiUrl()).toBe('http://localhost:8000');
    });
  });

  describe('getWsUrl', () => {
    it('should return VITE_WS_URL when set', async () => {
      vi.stubGlobal('location', {
        hostname: 'localhost',
        protocol: 'http:',
        host: 'localhost:5173',
      });

      vi.stubEnv('VITE_WS_URL', 'ws://custom-ws.example.com:3000');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getWsUrl } = await import('./network.js');
      expect(getWsUrl()).toBe('ws://custom-ws.example.com:3000');
    });

    it('should use wss protocol for https in production', async () => {
      vi.stubGlobal('location', {
        hostname: '192.168.1.100',
        protocol: 'https:',
        host: '192.168.1.100',
      });

      vi.stubEnv('VITE_WS_URL', '');
      vi.stubEnv('DEV', false);
      vi.stubEnv('PROD', true);

      const { getWsUrl } = await import('./network.js');
      expect(getWsUrl()).toBe('wss://192.168.1.100');
    });

    it('should use ws protocol for http in production', async () => {
      vi.stubGlobal('location', {
        hostname: '192.168.1.100',
        protocol: 'http:',
        host: '192.168.1.100',
      });

      vi.stubEnv('VITE_WS_URL', '');
      vi.stubEnv('DEV', false);
      vi.stubEnv('PROD', true);

      const { getWsUrl } = await import('./network.js');
      expect(getWsUrl()).toBe('ws://192.168.1.100');
    });

    it('should fallback to ws://localhost:8000 in dev mode when accessing from localhost', async () => {
      vi.stubGlobal('location', {
        hostname: 'localhost',
        protocol: 'http:',
        host: 'localhost:5173',
      });

      vi.stubEnv('VITE_WS_URL', '');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getWsUrl } = await import('./network.js');
      expect(getWsUrl()).toBe('ws://localhost:8000');
    });

    it('should use window.location.hostname:8000 in dev mode when accessed remotely', async () => {
      vi.stubGlobal('location', {
        hostname: '192.168.1.50',
        protocol: 'http:',
        host: '192.168.1.50:5173',
      });

      vi.stubEnv('VITE_WS_URL', '');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getWsUrl } = await import('./network.js');
      expect(getWsUrl()).toBe('ws://192.168.1.50:8000');
      expect(consoleWarnSpy).toHaveBeenCalled();
    });

    it('should use wss in dev mode when accessed remotely over https', async () => {
      vi.stubGlobal('location', {
        hostname: '192.168.1.50',
        protocol: 'https:',
        host: '192.168.1.50:5173',
      });

      vi.stubEnv('VITE_WS_URL', '');
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { getWsUrl } = await import('./network.js');
      expect(getWsUrl()).toBe('wss://192.168.1.50:8000');
    });
  });

  describe('isLocalhost', () => {
    it('should return true for localhost', async () => {
      vi.stubGlobal('location', { hostname: 'localhost', protocol: 'http:', host: 'localhost:5173' });
      const { isLocalhost } = await import('./network.js');
      expect(isLocalhost()).toBe(true);
    });

    it('should return true for 127.0.0.1', async () => {
      vi.stubGlobal('location', { hostname: '127.0.0.1', protocol: 'http:', host: '127.0.0.1:5173' });
      const { isLocalhost } = await import('./network.js');
      expect(isLocalhost()).toBe(true);
    });

    it('should return true for ::1', async () => {
      vi.stubGlobal('location', { hostname: '::1', protocol: 'http:', host: '[::1]:5173' });
      const { isLocalhost } = await import('./network.js');
      expect(isLocalhost()).toBe(true);
    });

    it('should return false for an IP address', async () => {
      vi.stubGlobal('location', { hostname: '192.168.1.50', protocol: 'http:', host: '192.168.1.50:5173' });
      const { isLocalhost } = await import('./network.js');
      expect(isLocalhost()).toBe(false);
    });

    it('should return false for a custom hostname', async () => {
      vi.stubGlobal('location', { hostname: 'my-raspberry-pi.local', protocol: 'http:', host: 'my-raspberry-pi.local:5173' });
      const { isLocalhost } = await import('./network.js');
      expect(isLocalhost()).toBe(false);
    });
  });

  describe('isRemoteDevAccess', () => {
    it('should return true in dev mode when accessed remotely', async () => {
      vi.stubGlobal('location', { hostname: '192.168.1.50', protocol: 'http:', host: '192.168.1.50:5173' });
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { isRemoteDevAccess } = await import('./network.js');
      expect(isRemoteDevAccess()).toBe(true);
    });

    it('should return false in dev mode when accessed from localhost', async () => {
      vi.stubGlobal('location', { hostname: 'localhost', protocol: 'http:', host: 'localhost:5173' });
      vi.stubEnv('DEV', true);
      vi.stubEnv('PROD', false);

      const { isRemoteDevAccess } = await import('./network.js');
      expect(isRemoteDevAccess()).toBe(false);
    });

    it('should return false in production mode', async () => {
      vi.stubGlobal('location', { hostname: '192.168.1.50', protocol: 'http:', host: '192.168.1.50:5173' });
      vi.stubEnv('DEV', false);
      vi.stubEnv('PROD', true);

      const { isRemoteDevAccess } = await import('./network.js');
      expect(isRemoteDevAccess()).toBe(false);
    });
  });

  describe('hasExplicitConfig', () => {
    it('should return true when both VITE_API_URL and VITE_WS_URL are set', async () => {
      vi.stubEnv('VITE_API_URL', 'http://example.com:8000');
      vi.stubEnv('VITE_WS_URL', 'ws://example.com:8000');

      const { hasExplicitConfig } = await import('./network.js');
      expect(hasExplicitConfig()).toBe(true);
    });

    it('should return false when only VITE_API_URL is set', async () => {
      vi.stubEnv('VITE_API_URL', 'http://example.com:8000');
      vi.stubEnv('VITE_WS_URL', '');

      const { hasExplicitConfig } = await import('./network.js');
      expect(hasExplicitConfig()).toBe(false);
    });

    it('should return false when neither are set', async () => {
      vi.stubEnv('VITE_API_URL', '');
      vi.stubEnv('VITE_WS_URL', '');

      const { hasExplicitConfig } = await import('./network.js');
      expect(hasExplicitConfig()).toBe(false);
    });
  });
});
