// utils/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export async function makeApiRequest(endpoint: string, options: RequestInit = {}) {
  try {
    console.log('Making request to:', `${API_BASE_URL}${endpoint}`); // Debug log

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
      mode: 'cors', // Add CORS mode
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Request failed');
    }

    return data;
  } catch (error) {
    console.error('API Request failed:', error); // Debug log
    throw error;
  }
}

export const authApi = {
  login: async (email: string, password: string) => {
    return makeApiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  register: async (email: string, password: string, name: string) => {
    return makeApiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  },

  verifyToken: async (token: string) => {
    return makeApiRequest('/api/auth/verify-token', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};