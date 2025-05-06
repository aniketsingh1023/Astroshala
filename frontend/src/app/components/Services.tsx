import { Card, CardContent } from "@/app/components/ui/card"
import { Star, Heart, DollarSign, Calendar, Compass, Moon } from "lucide-react"

const Services = () => {
  const services = [
    {
      icon: <Compass className="w-10 h-10 text-purple-600 dark:text-purple-400" />,
      title: "Career Guidance",
      description:
        "Get detailed insights about your professional path and opportunities based on your birth chart's 6th and 10th houses.",
    },
    {
      icon: <Heart className="w-10 h-10 text-purple-600 dark:text-purple-400" />,
      title: "Relationship Analysis",
      description: "Understand your relationships and marriage prospects through the analysis of 5th and 7th houses.",
    },
    {
      icon: <DollarSign className="w-10 h-10 text-purple-600 dark:text-purple-400" />,
      title: "Financial Forecast",
      description: "Discover your financial potential and wealth opportunities through 2nd and 11th house analysis.",
    },
    {
      icon: <Calendar className="w-10 h-10 text-purple-600 dark:text-purple-400" />,
      title: "Daily Predictions",
      description: "Receive personalized daily, weekly, and yearly horoscope predictions tailored to your birth chart.",
    },
    {
      icon: <Moon className="w-10 h-10 text-purple-600 dark:text-purple-400" />,
      title: "Spiritual Guidance",
      description: "Explore your spiritual path and karmic patterns through vedic astrological wisdom.",
    },
    {
      icon: <Star className="w-10 h-10 text-purple-600 dark:text-purple-400" />,
      title: "Remedial Solutions",
      description: "Get personalized remedies and solutions to overcome challenging planetary positions.",
    },
  ]

  return (
    <section id="services" className="py-20 bg-gray-50 dark:bg-gray-800">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Our Astrological Services
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Discover the power of Vedic astrology through our comprehensive range of services
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <Card
              key={index}
              className="group hover:shadow-lg transition-shadow duration-300 dark:bg-gray-700 dark:border-gray-600"
            >
              <CardContent className="p-6">
                <div className="mb-6 group-hover:scale-110 transition-transform duration-300">{service.icon}</div>
                <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">{service.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">{service.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Services
