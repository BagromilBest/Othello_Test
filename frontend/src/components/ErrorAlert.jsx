import React from 'react';

/**
 * Dismissible alert component for displaying success, info, warning, or error messages.
 * Used to surface errors from API calls, WebSocket connections, and other operations.
 */
const ErrorAlert = ({ 
  type = 'error', 
  title, 
  message, 
  action, 
  onDismiss,
  onAction,
  className = '',
}) => {
  // Define styles for each alert type
  const styles = {
    success: {
      bg: 'bg-green-600',
      icon: (
        <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      ),
      dismissColor: 'text-green-200 hover:text-white',
    },
    info: {
      bg: 'bg-blue-600',
      icon: (
        <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zm-1 9a1 1 0 001-1v-4a1 1 0 10-2 0v4a1 1 0 001 1z" clipRule="evenodd" />
        </svg>
      ),
      dismissColor: 'text-blue-200 hover:text-white',
    },
    warning: {
      bg: 'bg-yellow-600',
      icon: (
        <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      ),
      dismissColor: 'text-yellow-200 hover:text-white',
    },
    error: {
      bg: 'bg-red-600',
      icon: (
        <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      ),
      dismissColor: 'text-red-200 hover:text-white',
    },
  };

  const style = styles[type] || styles.error;

  return (
    <div 
      className={`${style.bg} text-white px-4 py-3 rounded-lg shadow-md ${className}`}
      role="alert"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start flex-1">
          {style.icon}
          <div className="flex-1">
            {title && <p className="font-medium">{title}</p>}
            {message && (
              <p className={`text-sm ${title ? 'mt-1' : ''}`}>{message}</p>
            )}
            {action && onAction && (
              <button
                onClick={onAction}
                className="mt-2 text-sm font-medium underline hover:no-underline"
              >
                {action}
              </button>
            )}
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={`ml-4 ${style.dismissColor}`}
            aria-label="Dismiss"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorAlert;
