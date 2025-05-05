import React from 'react';
import Header  from '@/app/components/Header';
import  Hero  from './components/Hero';
import  Services  from './components/Services';
import  {Button}  from '@/app/components/ui/button';

const MainPage = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Header with Navigation */}
      <Header />
      
      {/* Hero Section */}
      <Hero />
      
      {/* Features/Services Section */}
      <Services />
      
      {/* Call to Action Section */}
      <section className="py-20 bg-purple-50">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Begin Your Astrological Journey Today
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Get personalized insights about your life path, relationships, and career
            through ancient Vedic wisdom combined with modern technology.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-6 text-lg rounded-full"
            >
              Start Free Reading
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="px-8 py-6 text-lg rounded-full"
            >
              Learn More
            </Button>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">About Us</h3>
              <p className="text-gray-400">
                Combining ancient Vedic wisdom with modern technology for accurate astrological insights.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Services</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Birth Chart Analysis</li>
                <li>Career Guidance</li>
                <li>Relationship Compatibility</li>
                <li>Life Path Predictions</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Email: support@jyotish.com</li>
                <li>Phone: +1 (555) 123-4567</li>
                <li>Hours: 24/7 Support</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Follow Us</h3>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white">Twitter</a>
                <a href="#" className="text-gray-400 hover:text-white">Facebook</a>
                <a href="#" className="text-gray-400 hover:text-white">Instagram</a>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Parasara Jyotish. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainPage;