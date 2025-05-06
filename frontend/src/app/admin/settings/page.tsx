"use client"
import { useState } from "react"
import { Card, CardContent } from "@/app/components/ui/card"
import { Button } from "@/app/components/ui/button"
import { Switch } from "@/app/components/ui/switch"
import { useTheme } from "next-themes"
import { Moon, Sun, Globe, Lock, Shield } from "lucide-react"

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [privacy, setPrivacy] = useState({
    shareData: false,
    allowAnalytics: true,
  })

  const handleThemeChange = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  const handlePrivacyChange = (key: keyof typeof privacy) => {
    setPrivacy((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Settings</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-1">Manage your preferences and account settings</p>
      </div>

      <Card className="dark:bg-gray-900 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4 flex items-center">
            <Sun className="h-5 w-5 mr-2 text-yellow-500" />
            <Moon className="h-5 w-5 mr-2 text-purple-500" />
            Appearance
          </h2>

          <div className="flex items-center justify-between py-3">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Dark Mode</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Toggle between light and dark themes</p>
            </div>
            <Switch
              checked={theme === "dark"}
              onCheckedChange={handleThemeChange}
              className="data-[state=checked]:bg-purple-600"
            />
          </div>
        </CardContent>
      </Card>

      <Card className="dark:bg-gray-900 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4 flex items-center">
            <Shield className="h-5 w-5 mr-2 text-purple-600 dark:text-purple-400" />
            Privacy & Security
          </h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-700">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white">Share Birth Data</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Allow your birth data to be used for research (anonymized)
                </p>
              </div>
              <Switch
                checked={privacy.shareData}
                onCheckedChange={() => handlePrivacyChange("shareData")}
                className="data-[state=checked]:bg-purple-600"
              />
            </div>

            <div className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-700">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white">Analytics</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Allow usage data collection to improve our services
                </p>
              </div>
              <Switch
                checked={privacy.allowAnalytics}
                onCheckedChange={() => handlePrivacyChange("allowAnalytics")}
                className="data-[state=checked]:bg-purple-600"
              />
            </div>

            <div className="pt-2">
              <Button
                variant="outline"
                className="w-full flex items-center justify-center gap-2 dark:text-gray-300 dark:border-gray-600"
              >
                <Lock className="h-4 w-4" />
                Change Password
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="dark:bg-gray-900 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4 flex items-center">
            <Globe className="h-5 w-5 mr-2 text-purple-600 dark:text-purple-400" />
            Language & Region
          </h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-700">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white">Language</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">English (US)</p>
              </div>
              <Button variant="outline" size="sm" className="dark:text-gray-300 dark:border-gray-600">
                Change
              </Button>
            </div>

            <div className="flex items-center justify-between py-3">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white">Time Zone</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">UTC-05:00 Eastern Time (US & Canada)</p>
              </div>
              <Button variant="outline" size="sm" className="dark:text-gray-300 dark:border-gray-600">
                Change
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end space-x-4">
        <Button variant="outline" className="dark:text-gray-300 dark:border-gray-600">
          Cancel
        </Button>
        <Button className="bg-purple-600 hover:bg-purple-700 dark:bg-purple-700 dark:hover:bg-purple-800">
          Save Changes
        </Button>
      </div>
    </div>
  )
}
