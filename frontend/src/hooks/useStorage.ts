// hooks/useStorage.ts
import { useState, useEffect } from 'react';

export function useStorage() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const setItem = (key: string, value: string) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(key, value);
    }
  };

  const getItem = (key: string) => {
    if (typeof window !== 'undefined') {
      return window.localStorage.getItem(key);
    }
    return null;
  };

  const removeItem = (key: string) => {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(key);
    }
  };

  return {
    isClient,
    setItem,
    getItem,
    removeItem,
  };
}