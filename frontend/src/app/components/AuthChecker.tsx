// components/AuthChecker.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchWithAuth } from '@/utils/auth';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface AuthCheckerProps {
  children: React.ReactNode;
  redirectTo?: string;
  requireBirthDetails?: boolean;
}

const AuthChecker: React.FC<AuthCheckerProps> = ({
  children,
  redirectTo = '/auth/login',
  requireBirthDetails = false,
}) => {
  const router = useRouter();
  const [isVerifying, setIsVerifying] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const verifyAuth = async () => {
      try {
        // Check if token exists
        const token = localStorage.getItem('token');
        if (!token) {
          router.push(redirectTo);
          return;
        }

        // Verify token with backend
        const response = await fetchWithAuth(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/user/profile`);
        
        if (!response.ok) {
          throw new Error('Authentication failed');
        }

        const userData = await response.json();
        
        // Update user data in localStorage with latest from server
        localStorage.setItem('user_name', userData.name || '');
        localStorage.setItem('user_email', userData.email || '');
        localStorage.setItem('has_birth_details', 
          String(!!(userData.birth_details && 
                   userData.birth_details.date && 
                   userData.birth_details.time && 
                   userData.birth_details.place))
        );

        // If birth details are required but not available, redirect
        if (requireBirthDetails && 
            !(userData.birth_details && 
              userData.birth_details.date && 
              userData.birth_details.time && 
              userData.birth_details.place)) {
          router.push('/birth-details');
          return;
        }

        setIsAuthenticated(true);

      } catch (error) {
        // Clear auth data and redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_email');
        localStorage.removeItem('has_birth_details');
        
        if (error instanceof Error) {
          toast.error(error.message);
        }
        
        router.push(redirectTo);
      } finally {
        setIsVerifying(false);
      }
    };

    verifyAuth();
  }, [router, redirectTo, requireBirthDetails]);

  if (isVerifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-purple-50">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-purple-600" />
          <p className="text-gray-600">Verifying authentication...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : null;
};

export default AuthChecker;