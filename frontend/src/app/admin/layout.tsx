// app/admin/layout.tsx
'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { deleteCookie } from 'cookies-next';
import { 
  Star, 
  LogOut, 
  User, 
  MessageSquare, 
  Info, 
  Settings, 
  Menu,
  X,
  ChevronRight
} from 'lucide-react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = '/auth/login';
      return;
    }
    
    // Get user info
    const name = localStorage.getItem('user_name') || 'User';
    const email = localStorage.getItem('user_email') || '';
    setUserName(name);
    setUserEmail(email);

    // Check if on mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
      if (window.innerWidth < 1024) {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleLogout = () => {
    // Clear localStorage
    localStorage.clear();
    
    // Clear the auth cookie
    deleteCookie('token');
    
    // Redirect to login
    window.location.href = '/auth/login';
  };

  const navItems = [
    { path: '/admin/chat', label: 'Chat', icon: <MessageSquare size={20} /> },
    { path: '/admin/about', label: 'About', icon: <Info size={20} /> },
    { path: '/admin/profile', label: 'Profile', icon: <User size={20} /> },
    { path: '/admin/settings', label: 'Settings', icon: <Settings size={20} /> },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 py-3 px-4 lg:px-6 fixed top-0 left-0 right-0 z-30">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <button 
              className="lg:hidden mr-2 text-gray-500 hover:text-purple-600"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <div className="flex items-center">
              <Star className="h-7 w-7 text-purple-600 mr-2" />
              <h1 className="text-xl font-bold text-gray-800 hidden sm:block">Parasara Jyotish</h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex flex-col items-end">
              <span className="font-medium text-sm text-gray-900">{userName}</span>
              <span className="text-xs text-gray-500">{userEmail}</span>
            </div>
            <div className="bg-purple-100 rounded-full p-2">
              <User className="h-5 w-5 text-purple-600" />
            </div>
            <button
              onClick={handleLogout}
              className="text-gray-600 hover:text-red-600 bg-gray-100 hover:bg-red-50 rounded-full p-2 transition-colors"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Layout - Fixed the gap issue */}
      <div className="flex pt-16 flex-1">
        {/* Sidebar - Fixed width */}
        <aside 
          className={`${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
          } fixed lg:static top-16 bottom-0 left-0 w-64 bg-white border-r border-gray-200 z-20 transition-transform duration-300 ease-in-out`}
        >
          <nav className="p-4 space-y-1">
            {navItems.map((item) => (
              <Link 
                key={item.path} 
                href={item.path}
                className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                  pathname === item.path
                    ? 'bg-purple-50 text-purple-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-purple-600'
                }`}
              >
                {item.icon}
                <span className="ml-3">{item.label}</span>
                {pathname === item.path && (
                  <ChevronRight className="ml-auto h-4 w-4" />
                )}
              </Link>
            ))}
          </nav>
          
          <div className="absolute bottom-0 left-0 right-0 p-4">
            <div className="bg-purple-50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-purple-700 mb-1">Vedic Insight</h3>
              <p className="text-xs text-gray-600">
                "The planetary positions at birth reflect one's karma, actions, and possibilities."
              </p>
            </div>
          </div>
        </aside>

        {/* Main Content - Takes remaining space without gap */}
        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          {children}
        </main>
      </div>
      
      {/* Overlay for mobile sidebar */}
      {sidebarOpen && isMobile && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-10"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
}