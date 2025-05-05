// app/context/AuthContext.tsx
'use client';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  name: string;
  email: string;
  hasBirthDetails: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkBirthDetails: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check if user is logged in on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('user_id');
    const userName = localStorage.getItem('user_name');
    const userEmail = localStorage.getItem('user_email');
    const hasBirthDetails = localStorage.getItem('has_birth_details') === 'true';

    if (token && userId) {
      setUser({
        id: userId,
        name: userName || '',
        email: userEmail || '',
        hasBirthDetails
      });
    }

    setIsLoading(false);
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to log in');
      }

      // Save auth data
      localStorage.setItem('token', data.token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('user_name', data.name || '');
      localStorage.setItem('user_email', data.email);
      localStorage.setItem('has_birth_details', String(!!data.has_birth_details));

      setUser({
        id: data.user_id,
        name: data.name || '',
        email: data.email,
        hasBirthDetails: !!data.has_birth_details
      });

      // Redirect based on whether birth details exist
      if (data.has_birth_details) {
        router.push('/admin/chat');
      } else {
        router.push('/birth-details');
      }

    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
    localStorage.removeItem('has_birth_details');
    setUser(null);
    router.push('/auth/login');
  };

  // Check if user has birth details
  const checkBirthDetails = async (): Promise<boolean> => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        router.push('/auth/login');
        return false;
      }
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/user/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token expired or invalid
          logout();
          return false;
        }
        throw new Error('Failed to fetch user profile');
      }
      
      const data = await response.json();
      const hasBirthDetails = !!(data.birth_details && 
                              data.birth_details.date && 
                              data.birth_details.time && 
                              data.birth_details.place);
      
      // Update local storage and user state
      localStorage.setItem('has_birth_details', String(hasBirthDetails));
      
      if (user) {
        setUser({
          ...user,
          hasBirthDetails
        });
      }
      
      return hasBirthDetails;
      
    } catch (error) {
      console.error('Error checking birth details:', error);
      return false;
    }
  };

  const value = {
    user,
    isLoading,
    error,
    login,
    logout,
    checkBirthDetails
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}