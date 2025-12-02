import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Note: We need to mock performance.now() and the environment for testing

describe('timing utilities', () => {
  let consoleLogSpy;
  let consoleWarnSpy;
  let performanceNowMock;
  let currentTime = 0;

  beforeEach(() => {
    vi.resetModules();
    currentTime = 0;
    
    // Mock performance.now()
    performanceNowMock = vi.spyOn(performance, 'now').mockImplementation(() => currentTime);
    
    // Mock console methods
    consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    performanceNowMock.mockRestore();
    consoleLogSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  describe('startStage and endStage', () => {
    it('should record start time and compute duration', async () => {
      vi.stubEnv('DEV', true);
      
      const { startStage, endStage, getStageDuration, clearTimings } = await import('./timing.js');
      clearTimings();
      
      currentTime = 0;
      startStage('test_stage');
      
      currentTime = 150; // 150ms later
      const duration = endStage('test_stage');
      
      expect(duration).toBe(150);
      expect(getStageDuration('test_stage')).toBe(150);
    });

    it('should return null when ending a stage that was not started', async () => {
      vi.stubEnv('DEV', true);
      
      const { endStage, clearTimings } = await import('./timing.js');
      clearTimings();
      
      const duration = endStage('non_existent_stage');
      
      expect(duration).toBeNull();
      expect(consoleWarnSpy).toHaveBeenCalled();
    });

    it('should log in dev mode', async () => {
      vi.stubEnv('DEV', true);
      
      const { startStage, clearTimings } = await import('./timing.js');
      clearTimings();
      
      startStage('test_stage');
      
      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining('[Timing] Stage started: test_stage')
      );
    });
  });

  describe('logAndReport', () => {
    it('should start timing when no start time is provided', async () => {
      vi.stubEnv('DEV', true);
      
      const { logAndReport, clearTimings } = await import('./timing.js');
      clearTimings();
      
      currentTime = 100;
      const result = logAndReport('test_stage');
      
      expect(result).toBe(100);
    });

    it('should compute duration when start time is provided', async () => {
      vi.stubEnv('DEV', true);
      
      const { logAndReport, getStageDuration, clearTimings } = await import('./timing.js');
      clearTimings();
      
      currentTime = 250;
      const startTime = 100;
      const duration = logAndReport('test_stage', startTime);
      
      expect(duration).toBe(150);
      expect(getStageDuration('test_stage')).toBe(150);
    });
  });

  describe('getAllDurations and clearTimings', () => {
    it('should return all recorded durations', async () => {
      vi.stubEnv('DEV', true);
      
      const { startStage, endStage, getAllDurations, clearTimings } = await import('./timing.js');
      clearTimings();
      
      currentTime = 0;
      startStage('stage1');
      currentTime = 100;
      endStage('stage1');
      
      currentTime = 100;
      startStage('stage2');
      currentTime = 300;
      endStage('stage2');
      
      const durations = getAllDurations();
      
      expect(durations).toEqual({
        stage1: 100,
        stage2: 200,
      });
    });

    it('should clear all timings', async () => {
      vi.stubEnv('DEV', true);
      
      const { startStage, endStage, getAllDurations, clearTimings } = await import('./timing.js');
      
      currentTime = 0;
      startStage('stage1');
      currentTime = 100;
      endStage('stage1');
      
      clearTimings();
      
      const durations = getAllDurations();
      expect(durations).toEqual({});
    });
  });

  describe('getTimingSummary', () => {
    it('should return a formatted summary', async () => {
      vi.stubEnv('DEV', true);
      
      const { startStage, endStage, getTimingSummary, clearTimings } = await import('./timing.js');
      clearTimings();
      
      currentTime = 0;
      startStage('stage1');
      currentTime = 100;
      endStage('stage1');
      
      const summary = getTimingSummary();
      
      expect(summary).toContain('Initialization Timing Summary:');
      expect(summary).toContain('stage1: 100.00ms');
      expect(summary).toContain('Total: 100.00ms');
    });

    it('should return message when no data recorded', async () => {
      vi.stubEnv('DEV', true);
      
      const { getTimingSummary, clearTimings } = await import('./timing.js');
      clearTimings();
      
      const summary = getTimingSummary();
      
      expect(summary).toBe('No timing data recorded');
    });
  });

  describe('STAGES constants', () => {
    it('should export stage constants', async () => {
      const { STAGES } = await import('./timing.js');
      
      expect(STAGES.START_GAME_CLICK).toBe('start_game_click');
      expect(STAGES.MATCH_CREATION_API).toBe('match_creation_api');
      expect(STAGES.BOT_UPLOAD).toBe('bot_upload');
      expect(STAGES.WEBSOCKET_CONNECT).toBe('websocket_connect');
      expect(STAGES.WEBSOCKET_READY).toBe('websocket_ready');
      expect(STAGES.MATCH_CREATED).toBe('match_created');
      expect(STAGES.GAME_READY).toBe('game_ready');
    });
  });
});
