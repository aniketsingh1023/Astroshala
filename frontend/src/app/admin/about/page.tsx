"use client"
import { Card, CardContent } from "@/app/components/ui/card"
import { Calendar, Clock, MapPin, Star, BookOpen, History } from "lucide-react"

export default function AboutPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">About Parasara Jyotish</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-1">
          Your personal astrological consultation platform based on traditional Vedic principles
        </p>
      </div>

      <Card className="dark:bg-gray-900 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4 mb-6">
            <div className="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-full">
              <Star className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800 dark:text-white">Our Mission</h2>
              <p className="text-gray-600 dark:text-gray-300">
                To make ancient Vedic wisdom accessible in the modern age
              </p>
            </div>
          </div>

          <p className="text-gray-700 dark:text-gray-300 mb-6">
            Parasara Jyotish combines the deep insights of traditional Vedic astrology with modern technology to provide
            personalized astrological guidance. Named after Sage Parasara, the author of Brihat Parasara Hora Shastra,
            we aim to preserve and share this ancient knowledge system in an accessible way.
          </p>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <BookOpen className="h-5 w-5 text-purple-600 dark:text-purple-400 mr-2" />
                <h3 className="font-bold text-gray-800 dark:text-white">Vedic Foundations</h3>
              </div>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                Our platform draws from the principles outlined in classical Vedic texts, particularly the Brihat
                Parasara Hora Shastra, which forms the cornerstone of Hindu predictive astrology.
              </p>
            </div>

            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <History className="h-5 w-5 text-purple-600 dark:text-purple-400 mr-2" />
                <h3 className="font-bold text-gray-800 dark:text-white">Modern Approach</h3>
              </div>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                While honoring tradition, we use advanced computational techniques to perform complex astrological
                calculations with precision, making this ancient wisdom relevant for contemporary life.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="dark:bg-gray-900 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">Our Services</h2>

          <div className="space-y-6">
            <div className="flex items-start">
              <div className="bg-purple-100 dark:bg-purple-900/30 p-2 rounded-full mr-4 mt-1">
                <Calendar className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="font-bold text-gray-800 dark:text-white">Birth Chart Analysis</h3>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Discover insights from your unique planetary positions at birth. Our system analyzes your natal chart
                  based on precise birth details to reveal your inherent tendencies, strengths, and challenges.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="bg-purple-100 dark:bg-purple-900/30 p-2 rounded-full mr-4 mt-1">
                <Clock className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="font-bold text-gray-800 dark:text-white">Timing Predictions</h3>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Learn about auspicious periods and potential challenges in your life. Through dasha systems and
                  transit analysis, we provide insights into how planetary movements affect different periods of your
                  life.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="bg-purple-100 dark:bg-purple-900/30 p-2 rounded-full mr-4 mt-1">
                <MapPin className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="font-bold text-gray-800 dark:text-white">Astrological Consultations</h3>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Get answers to your specific questions through our AI-powered chat. Our system is trained on
                  traditional texts and can provide guidance on career, relationships, health, and spiritual growth from
                  a Vedic perspective.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="dark:bg-gray-900 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">How It Works</h2>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-purple-100 dark:bg-purple-900/30 rounded-full h-12 w-12 flex items-center justify-center mx-auto mb-3">
                <span className="text-purple-700 dark:text-purple-300 font-bold">1</span>
              </div>
              <h3 className="font-bold text-gray-800 dark:text-white mb-2">Enter Birth Details</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Provide accurate birth information including date, time, and place for precise chart calculation.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 dark:bg-purple-900/30 rounded-full h-12 w-12 flex items-center justify-center mx-auto mb-3">
                <span className="text-purple-700 dark:text-purple-300 font-bold">2</span>
              </div>
              <h3 className="font-bold text-gray-800 dark:text-white mb-2">AI Analysis</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Our system performs complex calculations and applies Vedic principles to your unique chart.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 dark:bg-purple-900/30 rounded-full h-12 w-12 flex items-center justify-center mx-auto mb-3">
                <span className="text-purple-700 dark:text-purple-300 font-bold">3</span>
              </div>
              <h3 className="font-bold text-gray-800 dark:text-white mb-2">Personalized Insights</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Receive customized astrological guidance through intuitive chat interface and reports.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="text-center text-sm text-gray-500 dark:text-gray-400 py-2">
        <p>© {new Date().getFullYear()} Parasara Jyotish. All rights reserved.</p>
      </div>
    </div>
  )
}
