/**
 * Centralized API Utility for Beehive Frontend
 * 
 * This module provides a clean, reusable wrapper around fetch for all API calls.
 * It handles authentication, error handling, and JSON parsing automatically.
 * 
 * @example Basic Usage
 * ```typescript
 * import { apiGet, apiPost, type GetTokenFn } from '@/utils/api';
 * import { useClerk } from '@clerk/clerk-react';
 * 
 * // Create token getter function
 * const { clerk } = useClerk();
 * const getToken: GetTokenFn = async () => {
 *   return await clerk.session?.getToken() || null;
 * };
 * 
 * // GET request
 * const users = await apiGet('/api/users', getToken);
 * 
 * // POST with JSON body
 * const newUser = await apiPost('/api/users', { name: 'John' }, getToken);
 * 
 * // POST with FormData
 * const formData = new FormData();
 * formData.append('image', file);
 * await apiPost('/api/upload', formData, getToken);
 * 
 * // PATCH and DELETE
 * await apiPatch('/api/users/1', { name: 'Jane' }, getToken);
 * await apiDelete('/api/users/1', getToken);
 * ```
 * 
 * @example Error Handling
 * ```typescript
 * try {
 *   const data = await apiGet('/api/users', getToken);
 * } catch (error) {
 *   if (error instanceof ApiError) {
 *     console.error(`API Error ${error.status}:`, error.message);
 *   }
 * }
 * ```
 */

// Centralized API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/**
 * Constructs the full API URL from a path
 * Kept for backward compatibility
 */
export const apiUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};

/**
 * Custom error class for API errors
 * Allows better error handling and messaging
 */
export class ApiError extends Error {
  status: number;
  data?: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Helper to get authentication token from Clerk
 * Returns null if not available
 */
export type GetTokenFn = () => Promise<string | null>;

/**
 * Core fetch wrapper with centralized error handling
 * Handles JSON parsing, error responses, and common headers
 */
async function apiFetch<T = any>(
  path: string,
  options: RequestInit = {},
  getToken?: GetTokenFn
): Promise<T> {
  const url = apiUrl(path);
  
  // Build headers with auth token if available
  const headers: HeadersInit = {
    ...options.headers,
  };

  // Add authorization header if token getter is provided
  if (getToken) {
    const token = await getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  // Make the request
  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // Include cookies for session management
  });

  // Handle non-JSON responses (e.g., file downloads)
  const contentType = response.headers.get('content-type');
  const isJson = contentType?.includes('application/json');

  // Parse response body
  let data: any;
  if (isJson) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  // Handle error responses
  if (!response.ok) {
    const errorMessage = 
      (isJson && data.error) || 
      (typeof data === 'string' && data) || 
      `HTTP ${response.status}: ${response.statusText}`;
    
    throw new ApiError(errorMessage, response.status, data);
  }

  // Check for application-level errors in successful responses
  if (isJson && data.error) {
    throw new ApiError(data.error, response.status, data);
  }

  return data;
}

/**
 * GET request helper
 * Usage: await apiGet('/api/users', getTokenFn)
 */
export async function apiGet<T = any>(
  path: string,
  getToken?: GetTokenFn
): Promise<T> {
  return apiFetch<T>(path, { method: 'GET' }, getToken);
}

/**
 * POST request helper
 * Automatically handles JSON serialization for objects
 * Usage: await apiPost('/api/users', { name: 'John' }, getTokenFn)
 */
export async function apiPost<T = any>(
  path: string,
  body?: any,
  getToken?: GetTokenFn
): Promise<T> {
  const isFormData = body instanceof FormData;
  
  return apiFetch<T>(
    path,
    {
      method: 'POST',
      headers: isFormData ? {} : { 'Content-Type': 'application/json' },
      body: isFormData ? body : JSON.stringify(body),
    },
    getToken
  );
}

/**
 * PATCH request helper
 * Automatically handles JSON serialization for objects
 * Usage: await apiPatch('/api/users/1', { name: 'Jane' }, getTokenFn)
 */
export async function apiPatch<T = any>(
  path: string,
  body?: any,
  getToken?: GetTokenFn
): Promise<T> {
  const isFormData = body instanceof FormData;
  
  return apiFetch<T>(
    path,
    {
      method: 'PATCH',
      headers: isFormData ? {} : { 'Content-Type': 'application/json' },
      body: isFormData ? body : JSON.stringify(body),
    },
    getToken
  );
}

/**
 * DELETE request helper
 * Usage: await apiDelete('/api/users/1', getTokenFn)
 */
export async function apiDelete<T = any>(
  path: string,
  getToken?: GetTokenFn
): Promise<T> {
  return apiFetch<T>(path, { method: 'DELETE' }, getToken);
}

/**
 * PUT request helper
 * Automatically handles JSON serialization for objects
 * Usage: await apiPut('/api/users/1', { name: 'Jane' }, getTokenFn)
 */
export async function apiPut<T = any>(
  path: string,
  body?: any,
  getToken?: GetTokenFn
): Promise<T> {
  const isFormData = body instanceof FormData;
  
  return apiFetch<T>(
    path,
    {
      method: 'PUT',
      headers: isFormData ? {} : { 'Content-Type': 'application/json' },
      body: isFormData ? body : JSON.stringify(body),
    },
    getToken
  );
}
