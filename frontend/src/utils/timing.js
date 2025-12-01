/**
 * Timing utility for recording and reporting initialization step durations.
 * Used for diagnosing slow game initialization on devices like Raspberry Pi.
 */

// Store named timestamps for computing durations
const timestamps = new Map();

// Store completed stage durations
const durations = new Map();

// Whether to show debug output
const isDebugEnabled = () => {
  return import.meta.env.DEV || import.meta.env.VITE_DEBUG === 'true';
};

/**
 * Record a timestamp for a named stage.
 * @param {string} stage - Name of the initialization stage
 */
export const startStage = (stage) => {
  timestamps.set(stage, performance.now());
  if (isDebugEnabled()) {
    console.log(`[Timing] Stage started: ${stage}`);
  }
};

/**
 * End a stage and compute its duration.
 * @param {string} stage - Name of the initialization stage
 * @returns {number|null} Duration in milliseconds, or null if stage wasn't started
 */
export const endStage = (stage) => {
  const startTime = timestamps.get(stage);
  if (startTime === undefined) {
    if (isDebugEnabled()) {
      console.warn(`[Timing] Attempted to end stage "${stage}" that was never started`);
    }
    return null;
  }

  const duration = performance.now() - startTime;
  durations.set(stage, duration);
  timestamps.delete(stage);

  if (isDebugEnabled()) {
    console.log(`[Timing] Stage completed: ${stage} - ${duration.toFixed(2)}ms`);
  }

  // Send to debug endpoint if configured
  const debugEndpoint = import.meta.env.VITE_DEBUG_ENDPOINT;
  if (debugEndpoint) {
    reportToEndpoint(stage, duration, debugEndpoint);
  }

  return duration;
};

/**
 * Log and report timing data. Convenience function for one-shot timing.
 * @param {string} stage - Name of the stage
 * @param {number} [startTime] - Optional start time (from performance.now())
 * @returns {number|null} Duration if startTime provided, or current timestamp if not
 */
export const logAndReport = (stage, startTime) => {
  if (startTime === undefined) {
    // Start new timing
    const now = performance.now();
    startStage(stage);
    return now;
  } else {
    // End timing using provided start time
    const duration = performance.now() - startTime;
    durations.set(stage, duration);

    if (isDebugEnabled()) {
      console.log(`[Timing] Stage completed: ${stage} - ${duration.toFixed(2)}ms`);
    }

    const debugEndpoint = import.meta.env.VITE_DEBUG_ENDPOINT;
    if (debugEndpoint) {
      reportToEndpoint(stage, duration, debugEndpoint);
    }

    return duration;
  }
};

/**
 * Get the duration of a completed stage.
 * @param {string} stage - Name of the stage
 * @returns {number|null} Duration in ms, or null if stage not found
 */
export const getStageDuration = (stage) => {
  return durations.get(stage) ?? null;
};

/**
 * Get all recorded durations.
 * @returns {Object} Map of stage names to durations
 */
export const getAllDurations = () => {
  return Object.fromEntries(durations);
};

/**
 * Clear all timing data.
 */
export const clearTimings = () => {
  timestamps.clear();
  durations.clear();
};

/**
 * Generate a summary report of all timings.
 * @returns {string} Formatted summary string
 */
export const getTimingSummary = () => {
  if (durations.size === 0) {
    return 'No timing data recorded';
  }

  const lines = ['Initialization Timing Summary:'];
  let total = 0;

  for (const [stage, duration] of durations) {
    lines.push(`  ${stage}: ${duration.toFixed(2)}ms`);
    total += duration;
  }

  lines.push(`  Total: ${total.toFixed(2)}ms`);
  return lines.join('\n');
};

/**
 * Log the timing summary to the console.
 */
export const logTimingSummary = () => {
  if (isDebugEnabled()) {
    console.log(getTimingSummary());
  }
};

/**
 * Send timing data to a debug endpoint.
 * @param {string} stage - Stage name
 * @param {number} duration - Duration in ms
 * @param {string} endpoint - URL to send data to
 */
const reportToEndpoint = async (stage, duration, endpoint) => {
  try {
    await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        stage,
        duration,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
      }),
    });
  } catch (error) {
    // Silently fail - debug endpoint is optional
    if (isDebugEnabled()) {
      console.warn(`[Timing] Failed to report to debug endpoint: ${error.message}`);
    }
  }
};

// Stage constants for consistent naming
export const STAGES = {
  START_GAME_CLICK: 'start_game_click',
  MATCH_CREATION_API: 'match_creation_api',
  BOT_UPLOAD: 'bot_upload',
  WEBSOCKET_CONNECT: 'websocket_connect',
  WEBSOCKET_READY: 'websocket_ready',
  MATCH_CREATED: 'match_created',
  GAME_READY: 'game_ready',
};
