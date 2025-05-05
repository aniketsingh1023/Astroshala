// app/auth/verify-email/page.tsx
'use client';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/app/components/ui/button';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Star, Loader2, CheckCircle, XCircle } from 'lucide-react';

const VerifyEmailPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');
      
      if (!token) {
        setStatus('error');
        setMessage('Verification token is missing');
        return;
      }

      try {
        console.log('Verifying token:', token);
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/verify-email`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });

        const data = await response.json();
        console.log('Verification response:', data);

        if (!response.ok) {
          throw new Error(data.error || 'Verification failed');
        }

        setStatus('success');
        setMessage('Email verified successfully!');

        // Redirect to login after 3 seconds
        setTimeout(() => {
          router.push('/auth/login');
        }, 3000);
        
      } catch (err: any) {
        console.error('Verification error:', err);
        setStatus('error');
        setMessage(err.message || 'Verification failed');
      }
    };

    verifyEmail();
  }, [router, searchParams]);

  return (
    <div className="min-h-screen bg-purple-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <Star className="h-12 w-12 text-purple-600" />
          <h1 className="mt-4 text-2xl font-bold">Email Verification</h1>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-center">Verifying Your Email</CardTitle>
          </CardHeader>
          <CardContent>
            {status === 'verifying' && (
              <div className="text-center space-y-4 py-8">
                <Loader2 className="h-12 w-12 animate-spin mx-auto text-purple-600" />
                <p className="text-gray-600">Verifying your email address...</p>
              </div>
            )}

            {status === 'success' && (
              <div className="text-center space-y-4 py-8">
                <CheckCircle className="h-12 w-12 mx-auto text-green-600" />
                <h3 className="text-xl font-medium text-gray-900">{message}</h3>
                <p className="text-gray-600">Redirecting to login page...</p>
              </div>
            )}

            {status === 'error' && (
              <div className="text-center space-y-4 py-6">
                <XCircle className="h-12 w-12 mx-auto text-red-600" />
                <h3 className="text-xl font-medium text-gray-900">Verification Failed</h3>
                <p className="text-gray-600">{message}</p>
                <div className="pt-4 space-y-3">
                  <Button
                    onClick={() => router.push(`/auth/resend-verification`)}
                    className="w-full"
                    variant="outline"
                  >
                    Resend Verification Email
                  </Button>
                  <Button
                    onClick={() => router.push('/auth/login')}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                  >
                    Return to Login
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VerifyEmailPage;