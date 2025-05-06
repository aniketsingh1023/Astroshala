import { NextResponse } from "next/server"

export async function POST(request: Request) {
  try {
    const data = await request.json()

    // Forward the request to your Flask backend
    const apiUrl = process.env.API_URL || "http://localhost:5001"
    const response = await fetch(`${apiUrl}/api/contact/submit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })

    const result = await response.json()

    if (!response.ok) {
      return NextResponse.json({ error: result.error || "Failed to submit contact form" }, { status: response.status })
    }

    return NextResponse.json(result)
  } catch (error) {
    console.error("Error in contact form submission:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
