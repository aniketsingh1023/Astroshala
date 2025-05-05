// app/auth/login/page.tsx
'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { Star } from 'lucide-react';
import { setCookie } from 'cookies-next'; // Make sure to install: npm install cookies-next

const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Create the API URL
      const apiUrl = 'http://localhost:5000/api/auth/login';
      
      // Make the fetch request
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      
      // Parse the JSON
      const data = await response.json();
      
      // Check if login was successful
      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }
      
      // Save auth data in localStorage
      localStorage.setItem('token', data.token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('user_name', data.name || '');
      localStorage.setItem('user_email', data.email);
      
      // IMPORTANT: Set token in cookie too (for middleware)
      setCookie('token', data.token, { maxAge: 60 * 60 * 24 }); // 24 hours
      
      // Use direct navigation
      window.location.href = '/admin/about';
      
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Test login function - for debugging only
  const testLogin = () => {
    // Create a test token
    const testToken = 'test-token-' + Date.now();
    
    // Save in localStorage
    localStorage.setItem('token', testToken);
    localStorage.setItem('user_id', 'test-id');
    localStorage.setItem('user_name', 'Test User');
    
    // IMPORTANT: Set in cookie too (for middleware)
    setCookie('token', testToken, { maxAge: 60 * 60 }); // 1 hour
    
    // Navigate
    window.location.href = '/admin/about';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-purple-50">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <Star className="h-12 w-12 text-purple-600" />
          <h1 className="mt-4 text-2xl font-bold text-gray-800">Welcome Back</h1>
          <p className="mt-2 text-gray-600">Sign in to your Parasara Jyotish account</p>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter your password"
              required
            />
          </div>
          
          <div className="flex items-center justify-between">
            <button
              type="submit"
              disabled={loading}
              className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full transition duration-150 ease-in-out"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </div>
        </form>

        {/* Test button for easy debugging */}
        <div className="mt-6 pt-6 border-t">
          <button
            onClick={testLogin}
            className="w-full bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded"
          >
            Test Login (Skip API)
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;