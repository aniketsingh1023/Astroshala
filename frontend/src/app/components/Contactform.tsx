"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/app/components/ui/button"

type FormData = {
  name: string
  email: string
  contactNumber: string
  birthDate: string
  birthTime: string
  birthPlace: string
  message: string
}

type FormErrors = {
  [key in keyof FormData]?: string
}

export default function ContactForm() {
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    contactNumber: "",
    birthDate: "",
    birthTime: "",
    birthPlace: "",
    message: "",
  })

  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<{
    success?: boolean
    message?: string
  }>({})

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = "Name is required"
    } else if (formData.name.trim().length < 2) {
      newErrors.name = "Name must be at least 2 characters"
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = "Email is required"
    } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address"
    }

    // Contact number validation
    if (!formData.contactNumber.trim()) {
      newErrors.contactNumber = "Contact number is required"
    } else if (formData.contactNumber.trim().length < 10) {
      newErrors.contactNumber = "Please enter a valid phone number"
    }

    // Birth date validation
    if (!formData.birthDate) {
      newErrors.birthDate = "Birth date is required"
    }

    // Birth time validation
    if (!formData.birthTime) {
      newErrors.birthTime = "Birth time is required"
    }

    // Birth place validation
    if (!formData.birthPlace.trim()) {
      newErrors.birthPlace = "Birth place is required"
    } else if (formData.birthPlace.trim().length < 2) {
      newErrors.birthPlace = "Birth place must be at least 2 characters"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))

    // Clear error when user types
    if (errors[name as keyof FormData]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setSubmitStatus({})

    try {
      // Try the direct endpoint first
      const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"}/api/contact/direct-submit`
      console.log("Submitting form to:", apiUrl)

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          contactNumber: formData.contactNumber,
          birthDate: formData.birthDate,
          birthTime: formData.birthTime,
          birthPlace: formData.birthPlace,
          message: formData.message,
          created_at: new Date().toISOString(),
        }),
      })

      const result = await response.json()
      console.log("Form submission result:", result)

      if (response.ok) {
        setSubmitStatus({
          success: true,
          message: "Form submitted successfully! We'll get back to you soon.",
        })

        // Reset form on success
        setFormData({
          name: "",
          email: "",
          contactNumber: "",
          birthDate: "",
          birthTime: "",
          birthPlace: "",
          message: "",
        })
      } else {
        setSubmitStatus({
          success: false,
          message: result.error || "There was a problem submitting your form.",
        })
      }
    } catch (error) {
      console.error("Error submitting form:", error)
      setSubmitStatus({
        success: false,
        message: "There was a problem connecting to the server. Please try again later.",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      {submitStatus.message && (
        <div
          className={`mb-6 p-4 rounded-md ${
            submitStatus.success
              ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
              : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
          }`}
        >
          {submitStatus.message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Name Field */}
          <div className="space-y-2">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Full Name
            </label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="John Doe"
              className={`w-full px-3 py-2 border rounded-md ${
                errors.name ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
            />
            {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
          </div>

          {/* Email Field */}
          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="john@example.com"
              className={`w-full px-3 py-2 border rounded-md ${
                errors.email ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
            />
            {errors.email && <p className="text-sm text-red-500">{errors.email}</p>}
          </div>

          {/* Contact Number Field */}
          <div className="space-y-2">
            <label htmlFor="contactNumber" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Contact Number
            </label>
            <input
              id="contactNumber"
              name="contactNumber"
              type="tel"
              value={formData.contactNumber}
              onChange={handleChange}
              placeholder="+1 (555) 123-4567"
              className={`w-full px-3 py-2 border rounded-md ${
                errors.contactNumber ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
            />
            {errors.contactNumber && <p className="text-sm text-red-500">{errors.contactNumber}</p>}
          </div>

          {/* Birth Date Field */}
          <div className="space-y-2">
            <label htmlFor="birthDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Birth Date
            </label>
            <input
              id="birthDate"
              name="birthDate"
              type="date"
              value={formData.birthDate}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md ${
                errors.birthDate ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
            />
            {errors.birthDate && <p className="text-sm text-red-500">{errors.birthDate}</p>}
          </div>

          {/* Birth Time Field */}
          <div className="space-y-2">
            <label htmlFor="birthTime" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Birth Time
            </label>
            <input
              id="birthTime"
              name="birthTime"
              type="time"
              value={formData.birthTime}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md ${
                errors.birthTime ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
            />
            {errors.birthTime && <p className="text-sm text-red-500">{errors.birthTime}</p>}
          </div>

          {/* Birth Place Field */}
          <div className="space-y-2">
            <label htmlFor="birthPlace" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Birth Place
            </label>
            <input
              id="birthPlace"
              name="birthPlace"
              type="text"
              value={formData.birthPlace}
              onChange={handleChange}
              placeholder="City, Country"
              className={`w-full px-3 py-2 border rounded-md ${
                errors.birthPlace ? "border-red-500" : "border-gray-300 dark:border-gray-600"
              } focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
            />
            {errors.birthPlace && <p className="text-sm text-red-500">{errors.birthPlace}</p>}
          </div>
        </div>

        {/* Message Field */}
        <div className="space-y-2">
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Message (Optional)
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            placeholder="Tell us about your specific questions or concerns..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>

        <Button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white py-6 text-lg rounded-full"
        >
          {isSubmitting ? "Submitting..." : "Submit Request"}
        </Button>
      </form>
    </div>
  )
}
