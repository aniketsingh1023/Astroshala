"use client"
import type React from "react"
import { useState, useEffect } from "react"
import { Card, CardContent } from "@/app/components/ui/card"
import { Button } from "@/app/components/ui/button"
import { Input } from "@/app/components/ui/input"
import { Calendar, User, Mail, Save, AlertCircle } from "lucide-react"

export default function ProfilePage() {
  const [userData, setUserData] = useState({
    name: "",
    email: "",
    birthDate: "",
    birthTime: "",
    birthPlace: "",
    latitude: "",
    longitude: "",
  })

  const [isEditing, setIsEditing] = useState(false)
  const [savingStatus, setSavingStatus] = useState<null | "saving" | "success" | "error">(null)

  useEffect(() => {
    const loadUserData = async () => {
      try {
        const token = localStorage.getItem("token")
        if (!token) return

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"}/api/user/profile`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) throw new Error("Failed to load profile")

        const data = await response.json()

        setUserData({
          name: data.name || "",
          email: data.email || "",
          birthDate: data.birth_details?.date || "",
          birthTime: data.birth_details?.time || "",
          birthPlace: data.birth_details?.place || "",
          latitude: data.birth_details?.latitude || "",
          longitude: data.birth_details?.longitude || "",
        })
      } catch (error) {
        console.error("Error loading profile:", error)
      }
    }

    loadUserData()
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setUserData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      setSavingStatus("saving")

      const token = localStorage.getItem("token")

      // Format birth details for the API
      const birthDetails = {
        date: userData.birthDate,
        time: userData.birthTime,
        place: userData.birthPlace,
        latitude: userData.latitude,
        longitude: userData.longitude,
      }

      // Send to server
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"}/api/user/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: userData.name,
          birth_details: birthDetails,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to update profile")
      }

      // Update local storage
      localStorage.setItem("user_name", userData.name)

      setSavingStatus("success")
      setIsEditing(false)

      setTimeout(() => setSavingStatus(null), 3000)
    } catch (error) {
      console.error("Error saving profile:", error)
      setSavingStatus("error")
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Your Profile</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-1">Manage your personal information and birth details</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-1">
          <Card className="dark:bg-gray-900">
            <CardContent className="p-6">
              <div className="flex flex-col items-center justify-center">
                <div className="bg-purple-100 dark:bg-purple-900/30 rounded-full p-6 mb-4">
                  <User className="h-12 w-12 text-purple-600 dark:text-purple-400" />
                </div>
                <h2 className="text-xl font-bold text-center text-gray-800 dark:text-white">{userData.name}</h2>
                <p className="text-gray-600 dark:text-gray-300 flex items-center mt-1">
                  <Mail className="h-4 w-4 mr-1" />
                  {userData.email}
                </p>
                <Button
                  className="mt-4 w-full"
                  variant={isEditing ? "outline" : "default"}
                  onClick={() => setIsEditing(!isEditing)}
                >
                  {isEditing ? "Cancel Editing" : "Edit Profile"}
                </Button>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Account Info</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Member Since</span>
                    <span className="text-gray-900 dark:text-gray-100">January 2023</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Account Type</span>
                    <span className="text-gray-900 dark:text-gray-100">Standard</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Status</span>
                    <span className="text-green-600 dark:text-green-400">Active</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2">
          <Card className="dark:bg-gray-900">
            <CardContent className="p-6">
              <form onSubmit={handleSubmit}>
                <div className="space-y-4">
                  <div>
                    <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">Personal Information</h2>

                    <div className="space-y-4">
                      <div>
                        <label
                          htmlFor="name"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                        >
                          Full Name
                        </label>
                        <Input
                          id="name"
                          name="name"
                          value={userData.name}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className="w-full dark:bg-gray-800 dark:text-white dark:border-gray-700"
                        />
                      </div>

                      <div>
                        <label
                          htmlFor="email"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                        >
                          Email Address
                        </label>
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          value={userData.email}
                          disabled={true} // Email is usually not editable
                          className="w-full bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600"
                        />
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                          Your email address cannot be changed
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="pt-6">
                    <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4 flex items-center">
                      <Calendar className="h-5 w-5 mr-2 text-purple-600 dark:text-purple-400" />
                      Birth Details
                    </h2>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
                      Accurate birth details are essential for precise astrological calculations
                    </p>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <label
                          htmlFor="birthDate"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                        >
                          Birth Date
                        </label>
                        <Input
                          id="birthDate"
                          name="birthDate"
                          type="date"
                          value={userData.birthDate}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className="w-full dark:bg-gray-800 dark:text-white dark:border-gray-700"
                        />
                      </div>

                      <div>
                        <label
                          htmlFor="birthTime"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                        >
                          Birth Time
                        </label>
                        <Input
                          id="birthTime"
                          name="birthTime"
                          type="time"
                          value={userData.birthTime}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className="w-full dark:bg-gray-800 dark:text-white dark:border-gray-700"
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label
                          htmlFor="birthPlace"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                        >
                          Birth Place
                        </label>
                        <Input
                          id="birthPlace"
                          name="birthPlace"
                          value={userData.birthPlace}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className="w-full dark:bg-gray-800 dark:text-white dark:border-gray-700"
                          placeholder="City, Country"
                        />
                      </div>

                      <div>
                        <label
                          htmlFor="latitude"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                        >
                          Latitude
                        </label>
                        <Input
                          id="latitude"
                          name="latitude"
                          value={userData.latitude}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className="w-full dark:bg-gray-800 dark:text-white dark:border-gray-700"
                        />
                      </div>

                      <div>
                        <label
                          htmlFor="longitude"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                        >
                          Longitude
                        </label>
                        <Input
                          id="longitude"
                          name="longitude"
                          value={userData.longitude}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className="w-full dark:bg-gray-800 dark:text-white dark:border-gray-700"
                        />
                      </div>
                    </div>
                  </div>

                  {isEditing && (
                    <div className="pt-4 flex justify-end">
                      <Button
                        type="submit"
                        className="bg-purple-600 hover:bg-purple-700 dark:bg-purple-700 dark:hover:bg-purple-800"
                        disabled={savingStatus === "saving"}
                      >
                        {savingStatus === "saving" ? (
                          <>
                            <Save className="h-4 w-4 mr-2 animate-spin" />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Save className="h-4 w-4 mr-2" />
                            Save Changes
                          </>
                        )}
                      </Button>
                    </div>
                  )}

                  {savingStatus === "success" && (
                    <div className="bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 p-3 rounded-md flex items-center">
                      <Save className="h-4 w-4 mr-2" />
                      Your profile has been updated successfully
                    </div>
                  )}

                  {savingStatus === "error" && (
                    <div className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 p-3 rounded-md flex items-center">
                      <AlertCircle className="h-4 w-4 mr-2" />
                      There was an error saving your profile. Please try again.
                    </div>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
