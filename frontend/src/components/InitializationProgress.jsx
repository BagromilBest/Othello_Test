import React, { useState, useEffect, useCallback } from 'react';

/**
 * Initialization progress overlay component.
 * Shows a horizontal progress bar and step labels for game initialization stages.
 */

// Default timeout for each stage in seconds
const DEFAULT_STAGE_TIMEOUT = 15;

// Initialization stages with labels
export const INIT_STAGES = [
  { id: 'starting', label: 'Starting' },
  { id: 'creating_match', label: 'Creating match' },
  { id: 'uploading_bots', label: 'Uploading bots' },
  { id: 'waiting_server', label: 'Waiting for server' },
  { id: 'connecting_websocket', label: 'Connecting WebSocket' },
  { id: 'ready', label: 'Ready' },
];

const InitializationProgress = ({
  currentStage,
  error = null,
  onRetry,
  onCancel,
  stageTimeout = DEFAULT_STAGE_TIMEOUT,
  stageDurations = {},
}) => {
  const [stalled, setStalled] = useState(false);
  const [stallTimeout, setStallTimeout] = useState(null);

  // Find the index of the current stage
  const currentIndex = INIT_STAGES.findIndex((s) => s.id === currentStage);
  const progress = currentIndex >= 0 ? ((currentIndex + 1) / INIT_STAGES.length) * 100 : 0;

  // Track stall detection
  useEffect(() => {
    // Clear previous timeout
    if (stallTimeout) {
      clearTimeout(stallTimeout);
    }

    // Don't set timeout for 'ready' stage or if there's an error
    if (currentStage === 'ready' || error) {
      setStalled(false);
      return;
    }

    // Set new timeout for stall detection
    const timeout = setTimeout(() => {
      setStalled(true);
    }, stageTimeout * 1000);

    setStallTimeout(timeout);

    return () => {
      if (timeout) {
        clearTimeout(timeout);
      }
    };
  }, [currentStage, stageTimeout, error]);

  // Format duration for display
  const formatDuration = (ms) => {
    if (ms === undefined || ms === null) return '';
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="init-progress-title"
    >
      <div className="bg-surface-light rounded-xl p-6 max-w-lg w-full mx-4 shadow-2xl">
        <h2
          id="init-progress-title"
          className="text-xl font-bold text-white mb-4 text-center"
        >
          {error ? 'Initialization Failed' : 'Initializing Game'}
        </h2>

        {/* Progress Bar */}
        {!error && (
          <div className="mb-6">
            <div className="h-2 bg-surface-lighter rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Stage Steps */}
        <div className="space-y-2 mb-6">
          {INIT_STAGES.map((stage, index) => {
            const isCompleted = currentIndex > index;
            const isCurrent = currentIndex === index;
            const isPending = currentIndex < index;
            const duration = stageDurations[stage.id];

            let statusIcon;
            let textColor = 'text-gray-500';

            if (error && isCurrent) {
              statusIcon = (
                <span className="w-5 h-5 flex items-center justify-center text-red-500">
                  ✕
                </span>
              );
              textColor = 'text-red-400';
            } else if (isCompleted) {
              statusIcon = (
                <span className="w-5 h-5 flex items-center justify-center text-green-500">
                  ✓
                </span>
              );
              textColor = 'text-green-400';
            } else if (isCurrent) {
              statusIcon = (
                <span className="w-5 h-5 flex items-center justify-center">
                  <span className="w-3 h-3 bg-primary rounded-full animate-pulse" />
                </span>
              );
              textColor = 'text-white';
            } else {
              statusIcon = (
                <span className="w-5 h-5 flex items-center justify-center text-gray-600">
                  ○
                </span>
              );
            }

            return (
              <div
                key={stage.id}
                className={`flex items-center justify-between ${textColor}`}
              >
                <div className="flex items-center">
                  {statusIcon}
                  <span className="ml-2">{stage.label}</span>
                </div>
                {duration !== undefined && (
                  <span className="text-xs text-gray-500">
                    {formatDuration(duration)}
                  </span>
                )}
              </div>
            );
          })}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/50 border border-red-700 rounded-lg p-3 mb-4">
            <p className="text-red-200 text-sm">{error}</p>
            <p className="text-red-300/70 text-xs mt-2">
              Try checking your network connection or see the README for troubleshooting.
            </p>
          </div>
        )}

        {/* Stall Warning */}
        {stalled && !error && (
          <div className="bg-yellow-900/50 border border-yellow-700 rounded-lg p-3 mb-4">
            <p className="text-yellow-200 text-sm">
              This stage is taking longer than expected ({stageTimeout}s).
            </p>
            <p className="text-yellow-300/70 text-xs mt-1">
              This may be due to a slow network or server. You can retry or wait.
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 justify-center">
          {(error || stalled) && onRetry && (
            <button
              onClick={onRetry}
              className="btn-primary px-6 py-2"
            >
              Retry
            </button>
          )}
          {onCancel && (
            <button
              onClick={onCancel}
              className="btn-secondary px-6 py-2"
            >
              Cancel
            </button>
          )}
        </div>

        {/* Debug Info */}
        {import.meta.env.DEV && Object.keys(stageDurations).length > 0 && (
          <div className="mt-4 pt-4 border-t border-surface-lighter">
            <p className="text-xs text-gray-500 text-center">
              Total:{' '}
              {formatDuration(
                Object.values(stageDurations).reduce((sum, d) => sum + (d || 0), 0)
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InitializationProgress;
