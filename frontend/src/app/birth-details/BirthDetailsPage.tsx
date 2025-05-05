// app/birth-details/page.tsx
'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/app/components/ui/card';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Star, Calendar, Clock, MapPin, Globe, Loader2 } from 'lucide-react';
import Header from '@/app/components/Header';

interface BirthDetails {
  date: string;
  time: string;
  place: string;
  latitude?: string;
  longitude?: string;
}

const BirthDetailsPage = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [geocoding, setGeocoding] = useState(false);
  const [birthDetails, setBirthDetails] = useState<BirthDetails>({
    date: '',
    time: '',
    place: '',
    latitude: '',
    longitude: ''
  });

  // Check if user is authenticated
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
    }
  }, [router]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setBirthDetails(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear coordinates when place changes
    if (name === 'place') {
      setBirthDetails(prev => ({
        ...prev,
        latitude: '',
        longitude: ''
      }));
    }
    
    setError('');
  };

  const handleSelectChange = (name: string, value: string) => {
    setBirthDetails(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const geocodePlace = async () => {
    if (!birthDetails.place || birthDetails.place.trim() === '') {
      setError('Please enter a place before geocoding');
      return;
    }
    
    setGeocoding(true);
    try {
      // In a production app, you'd call a real geocoding service
      // For demonstration, we'll simulate with a delay and fake coordinates
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Generate semi-random coordinates based on input to simulate real geocoding
      // This is just for demonstration - in a real app you would use a geocoding API
      const hash = birthDetails.place.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
      const latBase = 10 + (hash % 80); // Between 10 and 90
      const longBase = 70 + (hash % 110); // Between 70 and 180
      
      setBirthDetails(prev => ({
        ...prev,
        latitude: (latBase * 0.1).toFixed(4),
        longitude: (longBase * 0.1).toFixed(4)
      }));
    } catch (err) {
      console.error('Geocoding error:', err);
      setError('Failed to geocode location. Please enter coordinates manually.');
    } finally {
      setGeocoding(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // Validate inputs
    if (!birthDetails.date) {
      setError('Birth date is required');
      return;
    }
    if (!birthDetails.time) {
      setError('Birth time is required');
      return;
    }
    if (!birthDetails.place) {
      setError('Birth place is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Get token from localStorage
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication required');
      }

      // Send birth details to API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/user/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          birth_details: {
            date: birthDetails.date,
            time: birthDetails.time,
            place: birthDetails.place,
            latitude: birthDetails.latitude || '0',
            longitude: birthDetails.longitude || '0'
          }
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to save birth details');
      }

      // Store birth details in localStorage as well
      localStorage.setItem('birthDetails', JSON.stringify(birthDetails));

      // Show success state
      setSuccess(true);
      
      // Redirect to admin dashboard after a delay
      setTimeout(() => {
        router.push('/admin/chat');
      }, 2000);
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-purple-50">
      <Header />
      
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-md mx-auto">
          <div className="flex flex-col items-center mb-8">
            <Star className="h-12 w-12 text-purple-600" />
            <h1 className="mt-4 text-2xl font-bold">Your Birth Details</h1>
            <p className="mt-2 text-gray-600 text-center">
              Please provide accurate birth information for precise astrological readings
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Birth Information</CardTitle>
              <CardDescription>
                This information is essential for your personalized astrological chart
              </CardDescription>
            </CardHeader>
            <CardContent>
              {success ? (
                <div className="py-8 text-center space-y-4">
                  <div className="bg-green-100 p-4 rounded-full inline-flex mx-auto">
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" 
                      className="h-8 w-8 text-green-600" 
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path 
                        strokeLinecap="round" 
                        strokeLinejoin="round" 
                        strokeWidth={2} 
                        d="M5 13l4 4L19 7" 
                      />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">Birth Details Saved!</h3>
                  <p className="text-gray-600">Your astrological journey is about to begin.</p>
                  <p className="text-sm text-gray-500">Redirecting to your dashboard...</p>
                  <div className="flex justify-center mt-4">
                    <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Birth Date */}
                  <div className="space-y-2">
                    <label className="flex items-center text-sm font-medium">
                      <Calendar className="mr-2 h-4 w-4 text-gray-500" />
                      Birth Date
                    </label>
                    <Input
                      type="date"
                      name="date"
                      value={birthDetails.date}
                      onChange={handleInputChange}
                      required
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500">
                      Format: YYYY-MM-DD
                    </p>
                  </div>
                  
                  {/* Birth Time */}
                  <div className="space-y-2">
                    <label className="flex items-center text-sm font-medium">
                      <Clock className="mr-2 h-4 w-4 text-gray-500" />
                      Birth Time
                    </label>
                    <Input
                      type="time"
                      name="time"
                      value={birthDetails.time}
                      onChange={handleInputChange}
                      required
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500">
                      Format: 24-hour clock (e.g., 14:30 for 2:30 PM)
                    </p>
                  </div>
                  
                  {/* Birth Place */}
                  <div className="space-y-2">
                    <label className="flex items-center text-sm font-medium">
                      <MapPin className="mr-2 h-4 w-4 text-gray-500" />
                      Birth Place
                    </label>
                    <div className="flex space-x-2">
                      <Input
                        type="text"
                        name="place"
                        placeholder="City, Country"
                        value={birthDetails.place}
                        onChange={handleInputChange}
                        required
                        className="w-full"
                      />
                      <Button 
                        type="button" 
                        variant="outline" 
                        size="sm"
                        onClick={geocodePlace}
                        disabled={geocoding || !birthDetails.place}
                      >
                        {geocoding ? 
                          <Loader2 className="h-4 w-4 animate-spin mr-1" /> : 
                          <Globe className="h-4 w-4 mr-1" />
                        }
                        Locate
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500">
                      Enter the city and country of your birth
                    </p>
                  </div>
                  
                  {/* Latitude & Longitude */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">
                        Latitude
                      </label>
                      <Input
                        type="text"
                        name="latitude"
                        placeholder="e.g., 28.6139"
                        value={birthDetails.latitude}
                        onChange={handleInputChange}
                        className="w-full"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">
                        Longitude
                      </label>
                      <Input
                        type="text"
                        name="longitude"
                        placeholder="e.g., 77.2090"
                        value={birthDetails.longitude}
                        onChange={handleInputChange}
                        className="w-full"
                      />
                    </div>
                  </div>

                  {/* Additional details for better predictions */}
                  <div className="space-y-2 pt-2">
                    <h4 className="text-sm font-medium">Astrology System Preference</h4>
                    <Select 
                      onValueChange={(value) => handleSelectChange('system', value)}
                      defaultValue="parasara"
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select astrology system" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="parasara">Parasara (Traditional Vedic)</SelectItem>
                        <SelectItem value="jaimini">Jaimini</SelectItem>
                        <SelectItem value="western">Western</SelectItem>
                        <SelectItem value="nadi">Nadi Astrology</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Error display */}
                  {error && (
                    <Alert variant="destructive" className="mt-4">
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}
                  
                  <Button 
                    type="submit" 
                    className="w-full bg-purple-600 hover:bg-purple-700 mt-6"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Saving Details...
                      </>
                    ) : 'Continue to Dashboard'}
                  </Button>
                </form>
              )}
            </CardContent>
            {!success && (
              <CardFooter>
                <p className="text-xs text-gray-500 text-center w-full">
                  Your birth details are crucial for accurate astrological readings. 
                  We keep this information secure and confidential.
                </p>
              </CardFooter>
            )}
          </Card>
        </div>
      </main>
    </div>
  );
};

export default BirthDetailsPage;