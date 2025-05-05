// app/auth/verification-pending/page.tsx
'use client';
import React from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/app/components/ui/card';
import { Mail, Star } from 'lucide-react';

const VerificationPendingPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get('email') || '';

  return (
    <div className="min-h-screen bg-purple-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="flex flex-col items-center">
          <Star className="h-12 w-12 text-purple-600" />
          <h1 className="mt-4 text-2xl font-bold">Check Your Email</h1>
          <p className="mt-2 text-gray-600">We've sent you a verification link</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Verify Your Email</CardTitle>
            <CardDescription>
              Please check your inbox to verify your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-col items-center py-4">
              <div className="bg-purple-100 p-4 rounded-full mb-4">
                <Mail className="h-12 w-12 text-purple-600" />
              </div>
              <p className="text-center text-gray-600 max-w-xs">
                We've sent a verification email to <strong>{email}</strong>. 
                Please check your inbox and follow the instructions to verify your account.
              </p>
            </div>

            <div className="space-y-3">
              <Button 
                className="w-full"
                variant="outline"
                onClick={() => router.push(`/auth/resend-verification?email=${encodeURIComponent(email)}`)}
              >
                Resend Verification Email
              </Button>
              <Link href="/auth/login">
                <Button className="w-full bg-purple-600 hover:bg-purple-700">
                  Return to Login
                </Button>
              </Link>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm text-gray-500 text-center">
                <strong>Note:</strong> In development mode, verification links are printed to the server console.
                Check your backend terminal for the verification URL.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VerificationPendingPage;