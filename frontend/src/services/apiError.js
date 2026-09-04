/**
 * Custom API Error class for handling API errors consistently
 */
export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Error types for categorizing different error scenarios
 */
export const ErrorTypes = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  CONFLICT: 'CONFLICT',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
};

/**
 * Parse API error response and return appropriate error type and message
 */
export function parseApiError(error) {
  if (!error.response) {
    // Network error or request didn't reach server
    return {
      type: ErrorTypes.NETWORK_ERROR,
      message: 'Network error. Please check your connection.',
      status: null,
    };
  }

  const { status, data } = error.response;

  if (data?.error) {
    // Server returned structured error
    const { type, message } = data.error;
    return {
      type: type || ErrorTypes.UNKNOWN_ERROR,
      message: message || 'An error occurred',
      status,
    };
  }

  // Fallback based on HTTP status
  switch (status) {
    case 400:
      return {
        type: ErrorTypes.VALIDATION_ERROR,
        message: 'Invalid request data',
        status,
      };
    case 401:
      return {
        type: ErrorTypes.UNAUTHORIZED,
        message: 'Authentication required',
        status,
      };
    case 403:
      return {
        type: ErrorTypes.FORBIDDEN,
        message: 'You do not have permission to perform this action',
        status,
      };
    case 404:
      return {
        type: ErrorTypes.NOT_FOUND,
        message: 'Resource not found',
        status,
      };
    case 409:
      return {
        type: ErrorTypes.CONFLICT,
        message: 'Resource conflict',
        status,
      };
    case 422:
      return {
        type: ErrorTypes.VALIDATION_ERROR,
        message: data?.detail || 'Validation failed',
        status,
      };
    case 500:
      return {
        type: ErrorTypes.SERVER_ERROR,
        message: 'Server error. Please try again later',
        status,
      };
    default:
      return {
        type: ErrorTypes.UNKNOWN_ERROR,
        message: 'An unexpected error occurred',
        status,
      };
  }
}

/**
 * Get user-friendly error message based on error type
 */
export function getUserErrorMessage(errorType, defaultMessage = 'An error occurred') {
  const messages = {
    [ErrorTypes.NETWORK_ERROR]: 'Unable to connect to the server. Please check your internet connection.',
    [ErrorTypes.VALIDATION_ERROR]: 'Please check your input and try again.',
    [ErrorTypes.NOT_FOUND]: 'The requested resource was not found.',
    [ErrorTypes.UNAUTHORIZED]: 'Please log in to continue.',
    [ErrorTypes.FORBIDDEN]: 'You do not have permission to access this resource.',
    [ErrorTypes.CONFLICT]: 'This action conflicts with existing data.',
    [ErrorTypes.SERVER_ERROR]: 'Something went wrong on our end. Please try again later.',
    [ErrorTypes.UNKNOWN_ERROR]: defaultMessage,
  };

  return messages[errorType] || defaultMessage;
}
