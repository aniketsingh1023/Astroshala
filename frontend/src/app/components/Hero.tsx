import { Button } from "@/app/components/ui/button"
import { Sparkles } from "lucide-react"
import Link from "next/link"

const Hero = () => {
  return (
    <div className="relative pt-20 pb-24 bg-gradient-to-b from-purple-50 via-white to-white dark:from-purple-950/20 dark:via-gray-900 dark:to-gray-900">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-4 right-1/4 w-64 h-64 bg-purple-100 dark:bg-purple-900/30 rounded-full blur-3xl opacity-30 animate-pulse" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-100 dark:bg-blue-900/30 rounded-full blur-3xl opacity-30 animate-pulse delay-1000" />
      </div>

      <div className="container mx-auto px-4 relative">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center px-4 py-2 mb-8 rounded-full bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300">
            <Sparkles className="w-4 h-4 mr-2" />
            <span>Discover Your Cosmic Path</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-white mb-8 tracking-tight">
            Vedic Wisdom Meets
            <span className="text-purple-600 dark:text-purple-400"> Modern Technology</span>
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 leading-relaxed">
            Unlock the secrets of your destiny through ancient Parasara Jyotish wisdom. Get personalized insights about
            your career, relationships, and life path.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/contact">
              <Button
                size="lg"
                className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-6 text-lg rounded-full w-full sm:w-auto"
              >
                Get Your Reading
              </Button>
            </Link>
            <Link href="/contact">
              <Button size="lg" variant="outline" className="px-8 py-6 text-lg rounded-full w-full sm:w-auto">
                Learn More
              </Button>
            </Link>
          </div>

          {/* Trust indicators */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 items-center justify-center">
            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">10K+</div>
              <div className="text-gray-600 dark:text-gray-300">Readings</div>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">98%</div>
              <div className="text-gray-600 dark:text-gray-300">Accuracy</div>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">24/7</div>
              <div className="text-gray-600 dark:text-gray-300">Support</div>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">4.9★</div>
              <div className="text-gray-600 dark:text-gray-300">Rating</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Hero
