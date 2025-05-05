// utils/auth.ts
import { NextRouter } from 'next/router';
import { toast } from 'sonner'; // Assuming you're using sonner for toast notifications

interface LoginResponse {
  token: string;
  user_id: string;
  name: string;
  email: string;
  has_birth_details: boolean;
}

export async function loginUser(email: string, password: string): Promise<LoginResponse | null> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Invalid email or password');
    }

    // Store auth data in localStorage
    localStorage.setItem('token', data.token);
    localStorage.setItem('user_id', data.user_id);
    localStorage.setItem('user_name', data.name || '');
    localStorage.setItem('user_email', data.email);
    localStorage.setItem('has_birth_details', String(!!data.has_birth_details));

    return data;
  } catch (error) {
    if (error instanceof Error) {
      toast.error(error.message);
    }
    return null;
  }
}

export function logoutUser(router: NextRouter) {
  // Clear all auth data
  localStorage.removeItem('token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('user_name');
  localStorage.removeItem('user_email');
  localStorage.removeItem('has_birth_details');
  
  // Redirect to login page
  router.push('/auth/login');
}

export function getCurrentUser() {
  // This function should be called only in client components
  if (typeof window === 'undefined') {
    return null;
  }

  const token = localStorage.getItem('token');
  if (!token) {
    return null;
  }

  return {
    id: localStorage.getItem('user_id'),
    name: localStorage.getItem('user_name') || '',
    email: localStorage.getItem('user_email') || '',
    hasBirthDetails: localStorage.getItem('has_birth_details') === 'true'
  };
}

export function isAuthenticated() {
  if (typeof window === 'undefined') {
    return false;
  }
  return !!localStorage.getItem('token');
}

export function getAuthHeader() {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token');
  
  if (!token) {
    throw new Error('Authentication required');
  }

  const authOptions = {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  return fetch(url, authOptions);
}