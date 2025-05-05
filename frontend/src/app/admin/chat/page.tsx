"use client"
import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Button } from "@/app/components/ui/button"
import { Input } from "@/app/components/ui/input"
import { Card, CardContent } from "@/app/components/ui/card"
import { Loader2, Send, Bot, UserIcon, RotateCcw, Briefcase, Heart, Coins } from "lucide-react"
import axios from "axios"
import ReactMarkdown from "react-markdown"

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"

// Define types
interface BirthDetails {
  date?: string
  time?: string
  place?: string
  [key: string]: any // For any other properties
}

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: string
}

// Topic types for specialized advice
type AdviceTopic = "job" | "marriage" | "finance" | null

// Chat messages hook with unified API
const useChatMessages = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [birthDetails, setBirthDetails] = useState<BirthDetails>({})
  const [showTopicSelection, setShowTopicSelection] = useState(false)
  // Add conversation state to track the flow
  const [conversationState, setConversationState] = useState<
    "introduction" | "birth_details" | "basic_prompt" | "topic_selection" | "topic_advice"
  >("introduction")
  // Track if birth details have been collected
  const [birthDetailsCollected, setBirthDetailsCollected] = useState(false)

  // Configure axios instance
  const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      "Content-Type": "application/json",
    },
  })

  // Add auth token to requests if available
  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`
    }
  }, [])

  // Start a new conversation
  const startConversation = async (birthDetailsData: BirthDetails | null = null) => {
    try {
      setLoading(true)
      setError(null)

      // Reset conversation state to introduction
      setConversationState("introduction")
      setBirthDetailsCollected(false)
      setShowTopicSelection(false)

      // Use birth details if provided, otherwise use stored ones
      const details = birthDetailsData || birthDetails || {}

      // Store birth details if provided
      if (birthDetailsData) {
        setBirthDetails(birthDetailsData)
        if (Object.keys(birthDetailsData).length >= 3) {
          setBirthDetailsCollected(true)
        }
      }

      const token = localStorage.getItem("token")
      let response

      if (token) {
        // Try authenticated endpoint
        try {
          response = await api.post("/api/chat/start", { birth_details: details })
          setConversationId(response.data.conversation_id)

          // Add initial message
          const initialMessage: ChatMessage = {
            id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            role: "assistant",
            content:
              "Welcome to Parasara Jyotish consultation! I'm your astrological assistant. Before we begin, could you please tell me a little about yourself?",
            timestamp: new Date().toISOString(),
          }
          setMessages([initialMessage])
          setLoading(false)
          return
        } catch (error) {
          console.log("Authenticated endpoint failed, using unified endpoint")
        }
      }

      // Use the unified endpoint for new conversation
      response = await axios.post(`${API_BASE_URL}/api/chat/query`, {
        message: "Start conversation",
        birth_details: details,
        conversation_history: [],
      })

      // Store conversation ID if available
      if (response.data.conversation_id) {
        setConversationId(response.data.conversation_id)
      } else {
        setConversationId("session-" + Date.now())
      }

      // Add initial message
      const initialMessage: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content:
          "Welcome to Parasara Jyotish consultation! I'm your astrological assistant. Before we begin, could you please tell me a little about yourself?",
        timestamp: new Date().toISOString(),
      }

      setMessages([initialMessage])
    } catch (err: any) {
      console.error("Error starting conversation:", err)
      setError(err.response?.data?.error || err.message || "Failed to start conversation")

      // Fallback to mock response
      const mockResponse: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content:
          "Welcome to Parasara Jyotish! I'm your astrological assistant. Before we begin, could you please tell me a little about yourself?",
        timestamp: new Date().toISOString(),
      }

      setConversationId("mock-conversation-" + Date.now())
      setMessages([mockResponse])
    } finally {
      setLoading(false)
    }
  }

  // Request birth details after introduction
  const requestBirthDetails = async () => {
    try {
      setLoading(true)
      setConversationState("birth_details")

      const birthDetailsMessage: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content:
          "Thank you for sharing. For an accurate astrological reading, I'll need your birth details. Could you please provide your birth date, time, and place of birth?",
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, birthDetailsMessage])
    } catch (err) {
      console.error("Error requesting birth details:", err)
    } finally {
      setLoading(false)
    }
  }

  // Process basic prompt after birth details are collected
  const processBasicPrompt = async () => {
    try {
      setLoading(true)
      setConversationState("basic_prompt")

      // Create conversation history from previous messages
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }))

      // Add a message indicating birth chart generation
      const analyzingMsg: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content:
          "I'm analyzing your birth chart based on Vedic astrology principles. This will include your ascendant, moon sign, planetary positions, and key yogas in your chart...",
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, analyzingMsg])

      // Call the backend for comprehensive birth chart analysis
      const response = await axios.post(`${API_BASE_URL}/api/chat/query`, {
        message:
          "Please provide a comprehensive birth chart analysis based on my birth details. Include ascendant, moon sign, sun sign, houses, lords, yogas, doshas, and planetary strengths.",
        conversation_id: conversationId,
        conversation_history: conversationHistory,
        birth_details: birthDetails,
      })

      // Add response to messages
      const basicPromptMessage: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content: response.data.response,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, basicPromptMessage])

      // Move to topic selection after a delay to allow user to read the birth chart analysis
      setTimeout(() => {
        requestTopicSelection()
      }, 3000)
    } catch (err) {
      console.error("Error processing basic prompt:", err)

      // Fallback message
      const fallbackMessage: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content:
          "Based on your birth details, I've analyzed your Vedic birth chart. I can see your ascendant, planetary positions, and key yogas in your chart. There are several interesting patterns that influence different areas of your life. What specific area would you like more detailed guidance on?",
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, fallbackMessage])

      // Still move to topic selection
      setTimeout(() => {
        requestTopicSelection()
      }, 2000)
    } finally {
      setLoading(false)
    }
  }

  // Request topic selection
  const requestTopicSelection = async () => {
    try {
      setLoading(true)
      setConversationState("topic_selection")

      const topicSelectionMessage: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content:
          "Now that I've analyzed your birth chart, which specific area of your life would you like more detailed advice on? Please select one of the options below or ask a specific question.",
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, topicSelectionMessage])
      setShowTopicSelection(true)
    } catch (err) {
      console.error("Error requesting topic selection:", err)
    } finally {
      setLoading(false)
    }
  }

  // Request topic-specific advice
  const requestTopicAdvice = async (topic: AdviceTopic) => {
    if (!topic) return

    try {
      setLoading(true)
      setError(null)
      setShowTopicSelection(false)
      setConversationState("topic_advice")

      // Add user message to the UI immediately
      const topicMessages = {
        job: "I'd like advice about my career and professional life.",
        marriage: "I'd like advice about my marriage and relationships.",
        finance: "I'd like advice about my financial situation and wealth.",
      }

      const userMsg: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "user",
        content: topicMessages[topic],
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMsg])

      // Create conversation history from previous messages
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }))

      // Use the specialized topic endpoint
      const response = await axios.post(`${API_BASE_URL}/api/chat/query`, {
        message: topicMessages[topic],
        conversation_id: conversationId,
        conversation_history: conversationHistory,
        birth_details: birthDetails,
        topic: topic, // Add the topic parameter
      })

      // Process response
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content: response.data.response,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])

      // Show topic selection again after advice
      setTimeout(() => {
        setShowTopicSelection(true)
      }, 1000)
    } catch (err: any) {
      console.error("Error requesting topic advice:", err)
      setError(err.response?.data?.error || err.message || "Failed to get topic advice")

      // Fallback to mock response
      const mockResponse: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content: `I'd be happy to provide insights about your ${topic}. To give you the most accurate guidance, could you please share your birth details (date, time, and place of birth)?`,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, mockResponse])

      // Show topic selection again after advice
      setTimeout(() => {
        setShowTopicSelection(true)
      }, 1000)
    } finally {
      setLoading(false)
    }
  }

  // Send a message
  const sendMessage = async (content: string) => {
    try {
      setLoading(true)
      setError(null)
      setShowTopicSelection(false)

      // Add user message to the UI immediately
      const userMsg: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMsg])

      // If no conversation exists, start a new one
      if (!conversationId) {
        await startConversation()
      }

      // Check if we're in introduction state and need to move to birth details
      if (conversationState === "introduction") {
        await requestBirthDetails()
        return
      }

      // Check if message contains birth details when in birth_details state
      if (conversationState === "birth_details") {
        const extractedDetails = extractBirthDetails(content)
        if (extractedDetails) {
          // Update birth details
          const updatedDetails = { ...birthDetails, ...extractedDetails }
          setBirthDetails(updatedDetails)

          // Check if we have enough details
          if (Object.keys(updatedDetails).length >= 2) {
            setBirthDetailsCollected(true)

            // Confirm birth details
            const confirmationMsg: ChatMessage = {
              id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              role: "assistant",
              content: `Thank you for providing your birth details. I've recorded:\n- Date: ${updatedDetails.date || "Not provided"}\n- Time: ${updatedDetails.time || "Not provided"}\n- Place: ${updatedDetails.place || "Not provided"}\n\nNow I'll analyze your chart.`,
              timestamp: new Date().toISOString(),
            }

            setMessages((prev) => [...prev, confirmationMsg])

            // Process basic prompt
            setTimeout(() => {
              processBasicPrompt()
            }, 1500)
            return
          }
        }

        // If not enough birth details, ask again
        const askAgainMsg: ChatMessage = {
          id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          role: "assistant",
          content:
            "I still need more birth details. Please provide your complete birth date, time, and place of birth for an accurate reading.",
          timestamp: new Date().toISOString(),
        }

        setMessages((prev) => [...prev, askAgainMsg])
        return
      }

      // Create conversation history from previous messages
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }))

      // Use the unified chat endpoint
      const response = await axios.post(`${API_BASE_URL}/api/chat/query`, {
        message: content,
        conversation_id: conversationId,
        conversation_history: conversationHistory,
        birth_details: birthDetails,
      })

      // Store conversation ID if it's a new conversation
      if (
        response.data.conversation_id &&
        conversationId &&
        !conversationId.includes("mock") &&
        !conversationId.includes("session")
      ) {
        setConversationId(response.data.conversation_id)
      }

      // Process response
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content: response.data.response,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])

      // Show topic selection again if we're past the basic prompt stage
      if (conversationState === "topic_selection" || conversationState === "topic_advice") {
        setTimeout(() => {
          setShowTopicSelection(true)
        }, 1000)
      }
    } catch (err: any) {
      console.error("Error sending message:", err)
      setError(err.response?.data?.error || err.message || "Failed to send message")

      // Fallback to mock response
      const mockResponse: ChatMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        content: generateMockResponse(content),
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, mockResponse])
    } finally {
      setLoading(false)
    }
  }

  // Extract birth details from user message
  const extractBirthDetails = (message: string): BirthDetails | null => {
    // Simple pattern matching to extract birth details
    const datePattern = /(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2} [a-zA-Z]+ \d{2,4})/
    const timePattern = /(\d{1,2}:\d{2} ?(?:AM|PM)?|\d{1,2} ?(?:AM|PM))/i
    const placePattern = /(born in|birth place|place of birth|in) ([A-Za-z\s,]+)/i

    const dateMatch = message.match(datePattern)
    const timeMatch = message.match(timePattern)
    const placeMatch = message.match(placePattern)

    const details: BirthDetails = {}
    if (dateMatch) details.date = dateMatch[1]
    if (timeMatch) details.time = timeMatch[1]
    if (placeMatch) details.place = placeMatch[2]

    // Also check for common date formats in natural language
    if (!dateMatch && message.toLowerCase().includes("born on")) {
      const bornOnMatch = message.match(/born on\s+([A-Za-z\s\d,]+)/i)
      if (bornOnMatch) details.date = bornOnMatch[1]
    }

    if (Object.keys(details).length > 0) {
      return details
    }
    return null
  }

  // Generate a mock response based on the question (fallback)
  const generateMockResponse = (question: string): string => {
    question = question.toLowerCase()

    if (question.includes("planet") || question.includes("graha")) {
      return "In Vedic astrology, there are nine celestial bodies or grahas: Sun (Surya), Moon (Chandra), Mars (Mangal), Mercury (Budha), Jupiter (Guru), Venus (Shukra), Saturn (Shani), and the lunar nodes Rahu and Ketu. Each planet represents different energies and influences various aspects of life."
    } else if (question.includes("house") || question.includes("bhava")) {
      return "Vedic astrology divides a birth chart into 12 houses or bhavas, each governing different areas of life. The 1st house represents self and personality, 2nd house wealth, 3rd house siblings, 4th house mother and home, 5th house creativity and children, and so on."
    } else if (question.includes("zodiac") || question.includes("rashi")) {
      return "Vedic astrology uses the sidereal zodiac with 12 signs (rashis): Aries (Mesha), Taurus (Vrishabha), Gemini (Mithuna), Cancer (Karka), Leo (Simha), Virgo (Kanya), Libra (Tula), Scorpio (Vrishchika), Sagittarius (Dhanu), Capricorn (Makara), Aquarius (Kumbha), and Pisces (Meena)."
    } else if (question.includes("dasha") || question.includes("period")) {
      return "Parasara Jyotish uses the Vimshottari Dasha system to time events. This system divides life into planetary periods (dashas) and sub-periods (antardashas). The sequence is: Sun (6 years), Moon (10 years), Mars (7 years), Rahu (18 years), Jupiter (16 years), Saturn (19 years), Mercury (17 years), Ketu (7 years), and Venus (20 years)."
    }
    return "According to Parasara Jyotish principles, your question relates to the cosmic influences that shape our experiences. The planetary positions and their aspects form unique patterns that can provide insights into various life situations. Would you like to know more about a specific area of Vedic astrology?"
  }

  // Reset conversation
  const resetConversation = () => {
    setMessages([])
    setConversationId(null)
    setError(null)
    setShowTopicSelection(false)
    setBirthDetails({})
    setBirthDetailsCollected(false)
    setConversationState("introduction")
    startConversation()
  }

  // Update birth details
  const updateBirthDetails = (details: BirthDetails) => {
    setBirthDetails(details)
    if (Object.keys(details).length >= 2) {
      setBirthDetailsCollected(true)
    }
  }

  return {
    messages,
    loading,
    error,
    sendMessage,
    startConversation,
    resetConversation,
    birthDetails,
    updateBirthDetails,
    extractBirthDetails,
    requestTopicAdvice,
    showTopicSelection,
    setShowTopicSelection,
    conversationState,
  }
}

export default function ChatPage() {
  const {
    messages,
    loading,
    error,
    sendMessage,
    startConversation,
    resetConversation,
    extractBirthDetails,
    requestTopicAdvice,
    showTopicSelection,
  } = useChatMessages()
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Start conversation if no messages exist
  useEffect(() => {
    if (messages.length === 0) {
      startConversation()
    }
  }, [messages.length, startConversation])

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim() && !loading) {
      // Check if message contains birth details
      extractBirthDetails(inputValue)

      sendMessage(inputValue)
      setInputValue("")
    }
  }

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)]">
      <div className="mb-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Astrological Consultation</h1>
          <p className="text-gray-600">Ask questions and receive insights based on Vedic astrological principles</p>
        </div>
        <Button
          variant="outline"
          className="flex items-center gap-2 text-black"
          onClick={resetConversation}
          disabled={loading}
        >
          <RotateCcw size={16} />
          New Consultation
        </Button>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        {/* Messages container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-purple-50">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-black-500">
              <Bot size={48} className="mb-2 text-purple-400" />
              <p>Start your consultation by sending a message</p>
              <Button variant="outline" className="mt-4" onClick={() => startConversation()}>
                Start New Consultation
              </Button>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={`${message.id}-${index}`}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`flex items-start space-x-2 max-w-[85%] ${
                      message.role === "user" ? "flex-row-reverse space-x-reverse" : "flex-row"
                    }`}
                  >
                    <div
                      className={`p-2 rounded-full ${
                        message.role === "user" ? "bg-purple-600 text-white" : "bg-gray-200 text-gray-800"
                      }`}
                    >
                      {message.role === "user" ? <UserIcon size={20} /> : <Bot size={20} />}
                    </div>
                    <Card className={`${message.role === "user" ? "bg-purple-600" : "bg-white"}`}>
                      <CardContent className="p-3">
                        {message.role === "assistant" ? (
                          <div className="prose max-w-none text-black space-y-6">
                            <ReactMarkdown
                              components={{
                                // Enhanced heading formatting
                                h1: ({ ...props }) => <h1 className="text-2xl font-bold mt-8 mb-4" {...props} />,
                                h2: ({ ...props }) => <h2 className="text-xl font-bold mt-6 mb-3" {...props} />,
                                h3: ({ ...props }) => <h3 className="text-lg font-bold mt-5 mb-2" {...props} />,
                                h4: ({ ...props }) => <h4 className="text-base font-bold mt-4 mb-2" {...props} />,

                                // Enhanced paragraph spacing
                                p: ({ ...props }) => <p className="my-3" {...props} />,

                                // Enhanced list formatting
                                ul: ({ ...props }) => <ul className="list-disc pl-6 my-4 space-y-2" {...props} />,
                                // Style ordered lists with better numbering
                                ol: ({ ...props }) => (
                                  <ol className="list-decimal pl-6 my-4 space-y-2 font-medium" {...props} />
                                ),
                                // All list items get consistent styling
                                li: ({ ...props }) => <li className="my-2 pl-1" {...props} />,

                                // Enhanced horizontal rule
                                hr: ({ ...props }) => <hr className="my-6 border-t-2 border-gray-200" {...props} />,

                                // Enhanced strong and emphasis
                                strong: ({ ...props }) => <strong className="font-bold" {...props} />,
                                em: ({ ...props }) => <em className="italic" {...props} />,
                              }}
                            >
                              {message.content}
                            </ReactMarkdown>
                          </div>
                        ) : (
                          <p className="text-white">{message.content}</p>
                        )}
                        <div className={`text-xs mt-3 ${message.role === "user" ? "text-purple-200" : "text-black"}`}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              ))}

              {/* Topic Selection Buttons */}
              {showTopicSelection && !loading && (
                <div className="flex flex-col items-center justify-center my-6 space-y-4">
                  <p className="text-center text-gray-700 font-medium">What would you like advice on?</p>
                  <div className="flex flex-wrap justify-center gap-4">
                    <Button
                      onClick={() => requestTopicAdvice("job")}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-full flex items-center gap-2"
                    >
                      <Briefcase size={18} />
                      Career & Job
                    </Button>
                    <Button
                      onClick={() => requestTopicAdvice("marriage")}
                      className="bg-pink-600 hover:bg-pink-700 text-white px-6 py-2 rounded-full flex items-center gap-2"
                    >
                      <Heart size={18} />
                      Marriage & Relationships
                    </Button>
                    <Button
                      onClick={() => requestTopicAdvice("finance")}
                      className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-full flex items-center gap-2"
                    >
                      <Coins size={18} />
                      Finance & Wealth
                    </Button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">Or type your own question below</p>
                </div>
              )}
            </>
          )}

          {/* Loading indicator */}
          {loading && (
            <div className="flex justify-start">
              <Card className="bg-white">
                <CardContent className="p-3 flex items-center space-x-2">
                  <Loader2 size={16} className="animate-spin text-purple-600" />
                  <span className="text-gray-600">Interpreting...</span>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="flex justify-center">
              <Card className="bg-red-50 border-red-200">
                <CardContent className="p-3 text-red-600">
                  <p>Error: {error}</p>
                  <Button variant="outline" size="sm" className="mt-2" onClick={() => resetConversation()}>
                    Try Again
                  </Button>
                </CardContent>
              </Card>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Message input */}
        <form onSubmit={handleSubmit} className="p-4 border-t bg-white mt-auto">
          <div className="flex space-x-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your question here..."
              disabled={loading}
              className="flex-grow"
            />
            <Button
              type="submit"
              disabled={loading || !inputValue.trim()}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {loading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Your consultation is based on Vedic astrological principles and knowledge from ancient texts.
          </p>
        </form>
      </Card>
    </div>
  )
}
