// app/components/BirthDetailsModal.tsx
'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Calendar, Clock, MapPin, Globe, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { useAuth } from '@/context/AuthContext';

interface BirthDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface BirthDetails {
  date: string;
  time: string;
  place: string;
  latitude?: string;
  longitude?: string;
}

const BirthDetailsModal = ({ isOpen, onClose }: BirthDetailsModalProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [geocoding, setGeocoding] = useState(false);
  const [birthDetails, setBirthDetails] = useState<BirthDetails>({
    date: '',
    time: '',
    place: '',
    latitude: '',
    longitude: ''
  });
  const router = useRouter();
  const { checkBirthDetails } = useAuth();

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
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/user/birth-details`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          date: birthDetails.date,
          time: birthDetails.time,
          place: birthDetails.place,
          latitude: birthDetails.latitude || '0',
          longitude: birthDetails.longitude || '0'
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to save birth details');
      }

      // Update birth details status
      await checkBirthDetails();
      
      // Close modal and continue
      onClose();
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Your Birth Details</DialogTitle>
          <DialogDescription>
            Please provide accurate birth information for precise astrological readings.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
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

          {/* Error display */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="flex justify-end space-x-2 mt-4">
            <Button variant="outline" type="button" onClick={onClose}>
              Skip for Now
            </Button>
            <Button 
              type="submit" 
              className="bg-purple-600 hover:bg-purple-700"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : 'Save Details'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default BirthDetailsModal;