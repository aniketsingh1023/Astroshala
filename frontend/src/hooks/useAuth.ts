// hooks/useAuth.ts
import { useState, useEffect } from 'react';

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    if (typeof window !== 'undefined') {
      const token = window.localStorage.getItem('token');
      setIsAuthenticated(!!token);
    }
    setIsLoading(false);
  };

  const setAuth = (token: string, userId: string) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('token', token);
      window.localStorage.setItem('user_id', userId);
      setIsAuthenticated(true);
    }
  };

  const clearAuth = () => {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('token');
      window.localStorage.removeItem('user_id');
      setIsAuthenticated(false);
    }
  };

  return { isAuthenticated, isLoading, setAuth, clearAuth };
}