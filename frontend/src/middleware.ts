// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// This function can be marked `async` if using `await` inside
export function middleware(request: NextRequest) {
  // Get the pathname
  const { pathname } = request.nextUrl;
  
  console.log('Middleware running for path:', pathname);
  
  // Check for token in cookies (more reliable than localStorage in middleware)
  const token = request.cookies.get('token')?.value;
  
  // Check if the path is for authenticated users
  if (pathname.startsWith('/admin')) {
    // If no token, redirect to login
    if (!token) {
      console.log('No token found, redirecting to login');
      return NextResponse.redirect(new URL('/auth/login', request.url));
    }
    
    // Token exists, allow access to admin routes
    return NextResponse.next();
  }
  
  // For login/signup pages, redirect to admin if already authenticated
  if ((pathname.startsWith('/auth/login') || pathname.startsWith('/auth/signup')) && token) {
    console.log('User already authenticated, redirecting to admin');
    return NextResponse.redirect(new URL('/admin/about', request.url));
  }
  
  // Default: allow the request
  return NextResponse.next();
}

// Configure which paths the middleware runs on
export const config = {
  matcher: [
    // Match all routes that require auth checking
    '/admin/:path*',
    '/auth/login',
    '/auth/signup',
  ],
};