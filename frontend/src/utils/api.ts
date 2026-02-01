const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export const apiUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};
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

export type GetTokenFn = () => Promise<string | null>;

async function apiFetch<T = any>(
  path: string,
  options: RequestInit = {},
  getToken?: GetTokenFn
): Promise<T> {
  const url = apiUrl(path);
  
  const headers: HeadersInit = {
    ...options.headers,
  };

  if (getToken) {
    const token = await getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });

  const contentType = response.headers.get('content-type');
  const isJson = contentType?.includes('application/json');

  let data: any;
  if (isJson) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const errorMessage = 
      (isJson && data.error) || 
      (typeof data === 'string' && data) || 
      `HTTP ${response.status}: ${response.statusText}`;
    
    throw new ApiError(errorMessage, response.status, data);
  }

  if (isJson && data.error) {
    throw new ApiError(data.error, response.status, data);
  }

  return data;
}

export async function apiGet<T = any>(
  path: string,
  getToken?: GetTokenFn
): Promise<T> {
  return apiFetch<T>(path, { method: 'GET' }, getToken);
}

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

export async function apiDelete<T = any>(
  path: string,
  getToken?: GetTokenFn
): Promise<T> {
  return apiFetch<T>(path, { method: 'DELETE' }, getToken);
}

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

export async function apiGetBlob(
  path: string,
  getToken?: GetTokenFn
): Promise<Blob> {
  const url = apiUrl(path);
  
  const headers: HeadersInit = {};

  if (getToken) {
    const token = await getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    method: 'GET',
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    throw new ApiError(
      `Failed to fetch blob: ${response.statusText}`,
      response.status
    );
  }

  return response.blob();
}
