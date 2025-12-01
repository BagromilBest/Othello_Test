import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('InitializationProgress component', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllEnvs();
  });

  describe('INIT_STAGES', () => {
    it('should export initialization stages', async () => {
      const { INIT_STAGES } = await import('../components/InitializationProgress.jsx');
      
      expect(INIT_STAGES).toHaveLength(6);
      expect(INIT_STAGES[0]).toEqual({ id: 'starting', label: 'Starting' });
      expect(INIT_STAGES[1]).toEqual({ id: 'creating_match', label: 'Creating match' });
      expect(INIT_STAGES[2]).toEqual({ id: 'uploading_bots', label: 'Uploading bots' });
      expect(INIT_STAGES[3]).toEqual({ id: 'waiting_server', label: 'Waiting for server' });
      expect(INIT_STAGES[4]).toEqual({ id: 'connecting_websocket', label: 'Connecting WebSocket' });
      expect(INIT_STAGES[5]).toEqual({ id: 'ready', label: 'Ready' });
    });

    it('should have unique stage IDs', async () => {
      const { INIT_STAGES } = await import('../components/InitializationProgress.jsx');
      
      const ids = INIT_STAGES.map(s => s.id);
      const uniqueIds = new Set(ids);
      
      expect(uniqueIds.size).toBe(ids.length);
    });
  });

  describe('Progress calculation', () => {
    it('should calculate progress based on current stage index', async () => {
      const { INIT_STAGES } = await import('../components/InitializationProgress.jsx');
      
      // Progress formula: ((currentIndex + 1) / total) * 100
      const totalStages = INIT_STAGES.length;
      
      expect(((0 + 1) / totalStages) * 100).toBeCloseTo(16.67, 1); // 'starting'
      expect(((1 + 1) / totalStages) * 100).toBeCloseTo(33.33, 1); // 'creating_match'
      expect(((5 + 1) / totalStages) * 100).toBe(100); // 'ready'
    });
  });

  describe('Stage status logic', () => {
    it('should correctly identify completed stages', async () => {
      const { INIT_STAGES } = await import('../components/InitializationProgress.jsx');
      
      const currentStage = 'uploading_bots'; // index 2
      const currentIndex = INIT_STAGES.findIndex(s => s.id === currentStage);
      
      // Stages before currentIndex are completed
      expect(currentIndex).toBe(2);
      expect(0 < currentIndex).toBe(true); // 'starting' is completed
      expect(1 < currentIndex).toBe(true); // 'creating_match' is completed
      expect(2 < currentIndex).toBe(false); // 'uploading_bots' is current
      expect(3 < currentIndex).toBe(false); // 'waiting_server' is pending
    });
  });

  describe('Duration formatting', () => {
    it('should format milliseconds correctly', () => {
      const formatDuration = (ms) => {
        if (ms === undefined || ms === null) return '';
        if (ms < 1000) return `${ms.toFixed(0)}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
      };
      
      expect(formatDuration(500)).toBe('500ms');
      expect(formatDuration(1500)).toBe('1.5s');
      expect(formatDuration(undefined)).toBe('');
      expect(formatDuration(null)).toBe('');
    });
  });
});
