import React, { useState } from 'react';
import { isRemoteDevAccess, hasExplicitConfig } from '../utils/network';

/**
 * Warning banner displayed when the app is accessed remotely in dev mode
 * without explicit VITE_API_URL/VITE_WS_URL configuration.
 */
const NetworkWarning = () => {
  const [dismissed, setDismissed] = useState(false);

  // Only show warning in dev mode when accessed remotely and without explicit config
  if (!isRemoteDevAccess() || hasExplicitConfig() || dismissed) {
    return null;
  }

  return (
    <div className="bg-yellow-600 text-white px-4 py-3 mb-4 rounded-lg shadow-md relative">
      <div className="flex items-start justify-between">
        <div className="flex items-center">
          <svg 
            className="w-5 h-5 mr-2 flex-shrink-0" 
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path 
              fillRule="evenodd" 
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" 
              clipRule="evenodd" 
            />
          </svg>
          <div>
            <p className="font-medium">Remote Development Mode</p>
            <p className="text-sm mt-1">
              Frontend running in development mode and accessed remotely. 
              Using server host for API/WS connections. 
              To configure explicitly, set <code className="bg-yellow-700 px-1 rounded">VITE_API_URL</code> and{' '}
              <code className="bg-yellow-700 px-1 rounded">VITE_WS_URL</code> in your <code className="bg-yellow-700 px-1 rounded">.env</code> file.
            </p>
          </div>
        </div>
        <button 
          onClick={() => setDismissed(true)} 
          className="ml-4 text-yellow-200 hover:text-white"
          aria-label="Dismiss warning"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path 
              fillRule="evenodd" 
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
              clipRule="evenodd" 
            />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default NetworkWarning;
