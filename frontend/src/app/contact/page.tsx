import Header from "@/app/components/Header"
import ContactForm from "@/app/components/Contactform"

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <Header />
      <div className="pt-24 pb-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">Contact Us</h1>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Get in touch for your personalized astrological reading
              </p>
            </div>

            <ContactForm />
          </div>
        </div>
      </div>

      {/* Simple Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 Parasara Jyotish. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
