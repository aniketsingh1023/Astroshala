// app/admin/settings/page.tsx
'use client';
import React, { useState } from 'react';
import { Card, CardContent } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { 
  Settings, 
  Bell, 
  Shield, 
  Languages, 
  Moon, 
  Sun,
  Check,
  Lock,
  Save
} from 'lucide-react';

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    email: true,
    app: true,
    marketing: false
  });
  
  const [theme, setTheme] = useState('light');
  const [language, setLanguage] = useState('english');
  const [savingSection, setSavingSection] = useState<string | null>(null);

  const handleNotificationChange = (type: keyof typeof notifications) => {
    setNotifications(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  const saveSettings = async (section: string) => {
    setSavingSection(section);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setSavingSection(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
        <p className="text-gray-600 mt-1">
          Customize your experience and manage your account preferences
        </p>
      </div>

      {/* Account Settings */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <Settings className="h-5 w-5 text-purple-600 mr-2" />
            <h2 className="text-xl font-bold text-gray-800">Account Settings</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <Input
                value="astrouser"
                disabled
                className="w-full md:w-1/2 bg-gray-50"
              />
              <p className="text-xs text-gray-500 mt-1">Username cannot be changed</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Account Email
              </label>
              <Input
                value="user@example.com"
                disabled
                className="w-full md:w-1/2 bg-gray-50"
              />
            </div>
            
            <div className="pt-2">
              <Button
                variant="outline"
                className="text-purple-600 border-purple-200 hover:bg-purple-50"
              >
                <Lock className="h-4 w-4 mr-2" />
                Change Password
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <Bell className="h-5 w-5 text-purple-600 mr-2" />
            <h2 className="text-xl font-bold text-gray-800">Notification Settings</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">Email Notifications</h3>
                <p className="text-sm text-gray-500">Receive emails for important updates</p>
              </div>
              <button
                onClick={() => handleNotificationChange('email')}
                title="Toggle Email Notifications"
                aria-label="Toggle Email Notifications"
                className={`w-10 h-6 rounded-full flex items-center transition-colors duration-300 focus:outline-none ${
                  notifications.email ? 'bg-purple-600 justify-end' : 'bg-gray-300 justify-start'
                }`}
              >
                <span className={`w-5 h-5 rounded-full bg-white shadow-md transform transition-transform duration-300 ${
                  notifications.email ? 'translate-x-0.5' : '-translate-x-0.5'
                }`}></span>
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">App Notifications</h3>
                <p className="text-sm text-gray-500">Receive in-app notifications</p>
              </div>
              <button
                onClick={() => handleNotificationChange('app')}
                title="Toggle App Notifications"
                aria-label="Toggle App Notifications"
                className={`w-10 h-6 rounded-full flex items-center transition-colors duration-300 focus:outline-none ${
                  notifications.app ? 'bg-purple-600 justify-end' : 'bg-gray-300 justify-start'
                }`}
              >
                <span className={`w-5 h-5 rounded-full bg-white shadow-md transform transition-transform duration-300 ${
                  notifications.app ? 'translate-x-0.5' : '-translate-x-0.5'
                }`}></span>
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">Marketing Emails</h3>
                <p className="text-sm text-gray-500">Receive promotional content and offers</p>
              </div>
              <button
                onClick={() => handleNotificationChange('marketing')}
                title="Toggle Marketing Emails"
                aria-label="Toggle Marketing Emails"
                className={`w-10 h-6 rounded-full flex items-center transition-colors duration-300 focus:outline-none ${
                  notifications.marketing ? 'bg-purple-600 justify-end' : 'bg-gray-300 justify-start'
                }`}
              >
                <span className={`w-5 h-5 rounded-full bg-white shadow-md transform transition-transform duration-300 ${
                  notifications.marketing ? 'translate-x-0.5' : '-translate-x-0.5'
                }`}></span>
              </button>
            </div>
            
            <div className="pt-2 flex justify-end">
              <Button
                onClick={() => saveSettings('notifications')}
                disabled={savingSection === 'notifications'}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {savingSection === 'notifications' ? (
                  <>
                    <Save className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Preferences
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Appearance & Language */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center mb-4">
            <Shield className="h-5 w-5 text-purple-600 mr-2" />
            <h2 className="text-xl font-bold text-gray-800">Appearance & Language</h2>
          </div>
          
          <div className="space-y-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Theme</h3>
              <div className="flex space-x-4">
                <button
                  onClick={() => setTheme('light')}
                  className={`p-3 rounded-lg flex flex-col items-center ${
                    theme === 'light' ? 'bg-purple-50 ring-2 ring-purple-600' : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <Sun className={`h-8 w-8 mb-2 ${theme === 'light' ? 'text-purple-600' : 'text-gray-400'}`} />
                  <span className={theme === 'light' ? 'text-purple-800 font-medium' : 'text-gray-700'}>Light</span>
                  {theme === 'light' && (
                    <Check className="h-4 w-4 text-purple-600 mt-2" />
                  )}
                </button>
                
                <button
                  onClick={() => setTheme('dark')}
                  className={`p-3 rounded-lg flex flex-col items-center ${
                    theme === 'dark' ? 'bg-purple-50 ring-2 ring-purple-600' : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <Moon className={`h-8 w-8 mb-2 ${theme === 'dark' ? 'text-purple-600' : 'text-gray-400'}`} />
                  <span className={theme === 'dark' ? 'text-purple-800 font-medium' : 'text-gray-700'}>Dark</span>
                  {theme === 'dark' && (
                    <Check className="h-4 w-4 text-purple-600 mt-2" />
                  )}
                </button>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Language</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {['english', 'hindi', 'sanskrit', 'spanish'].map((lang) => (
                  <button
                    key={lang}
                    onClick={() => setLanguage(lang)}
                    className={`py-2 px-3 rounded-lg flex items-center justify-center ${
                      language === lang 
                        ? 'bg-purple-50 ring-2 ring-purple-600 text-purple-800 font-medium' 
                        : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <Languages className={`h-4 w-4 mr-2 ${language === lang ? 'text-purple-600' : 'text-gray-400'}`} />
                    {lang.charAt(0).toUpperCase() + lang.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="pt-2 flex justify-end">
              <Button
                onClick={() => saveSettings('appearance')}
                disabled={savingSection === 'appearance'}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {savingSection === 'appearance' ? (
                  <>
                    <Save className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Settings
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200">
        <CardContent className="p-6">
          <h2 className="text-xl font-bold text-red-600 mb-4">Danger Zone</h2>
          
          <div className="space-y-4">
            <div className="flex items-start">
              <div>
                <h3 className="font-medium text-gray-900">Delete Account</h3>
                <p className="text-sm text-gray-500 max-w-xl">
                  Permanently delete your account and all associated data. This action cannot be undone.
                </p>
              </div>
            </div>
            
            <Button
              variant="outline"
              className="border-red-300 text-red-600 hover:bg-red-50"
            >
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}