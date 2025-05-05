// hooks/useChat.ts
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { fetchWithAuth, getCurrentUser } from '@/utils/auth';
import { toast } from 'sonner'; // Assuming you're using sonner for toast

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatState {
  loading: boolean;
  error: string | null;
  messages: Message[];
  conversationId: string | null;
}

export function useChat() {
  const router = useRouter();
  const [chatState, setChatState] = useState<ChatState>({
    loading: false,
    error: null,
    messages: [],
    conversationId: null,
  });
  
  // Start a new conversation
  const startConversation = useCallback(async () => {
    setChatState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const user = getCurrentUser();
      if (!user) {
        router.push('/auth/login');
        return;
      }
      
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat/start`;
      const response = await fetchWithAuth(apiUrl, {
        method: 'POST',
        body: JSON.stringify({
          // Include birth details from user state if needed for astrological analysis
          birth_details: user.hasBirthDetails ? JSON.parse(localStorage.getItem('birthDetails') || '{}') : {}
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to start conversation');
      }
      
      setChatState(prev => ({
        ...prev,
        loading: false,
        conversationId: data.conversation_id,
        messages: [
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: data.initial_response,
            timestamp: new Date().toISOString(),
          }
        ],
      }));
      
      // Store the conversation ID for persistence
      localStorage.setItem('currentConversationId', data.conversation_id);
      
    } catch (error) {
      if (error instanceof Error) {
        setChatState(prev => ({
          ...prev,
          loading: false,
          error: error.message,
        }));
        toast.error(error.message);
      }
    }
  }, [router]);
  
  // Send a message in an existing conversation
  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;
    
    setChatState(prev => ({ 
      ...prev, 
      loading: true, 
      error: null,
      messages: [
        ...prev.messages,
        {
          id: Date.now().toString(),
          role: 'user',
          content: message,
          timestamp: new Date().toISOString(),
        }
      ]
    }));
    
    try {
      // Ensure we have a conversation
      const conversationId = chatState.conversationId || localStorage.getItem('currentConversationId');
      
      if (!conversationId) {
        await startConversation();
      }
      
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat/continue`;
      const response = await fetchWithAuth(apiUrl, {
        method: 'POST',
        body: JSON.stringify({
          conversation_id: conversationId,
          message: message,
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to send message');
      }
      
      // Add assistant response to messages
      setChatState(prev => ({
        ...prev,
        loading: false,
        conversationId: data.conversation_id,
        messages: [
          ...prev.messages,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: data.response,
            timestamp: new Date().toISOString(),
          }
        ],
      }));
      
    } catch (error) {
      if (error instanceof Error) {
        setChatState(prev => ({
          ...prev,
          loading: false,
          error: error.message,
        }));
        toast.error(error.message);
      }
    }
  }, [chatState.conversationId, startConversation]);
  
  // Load chat history for a specific conversation
  const loadChatHistory = useCallback(async (conversationId: string) => {
    setChatState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat/history?conversation_id=${conversationId}`;
      const response = await fetchWithAuth(apiUrl);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to load chat history');
      }
      
      setChatState(prev => ({
        ...prev,
        loading: false,
        conversationId: conversationId,
        messages: data.messages || [],
      }));
      
      // Update the current conversation ID
      localStorage.setItem('currentConversationId', conversationId);
      
    } catch (error) {
      if (error instanceof Error) {
        setChatState(prev => ({
          ...prev,
          loading: false,
          error: error.message,
        }));
        toast.error(error.message);
      }
    }
  }, []);
  
  // Load user's conversation list
  const loadConversations = useCallback(async () => {
    try {
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat/conversations`;
      const response = await fetchWithAuth(apiUrl);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to load conversations');
      }
      
      return data.conversations || [];
      
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      }
      return [];
    }
  }, []);
  
  // Try to load existing conversation or start a new one on mount
  useEffect(() => {
    const savedConversationId = localStorage.getItem('currentConversationId');
    
    if (savedConversationId) {
      loadChatHistory(savedConversationId);
    } else {
      startConversation();
    }
  }, [startConversation, loadChatHistory]);
  
  return {
    ...chatState,
    sendMessage,
    startConversation,
    loadChatHistory,
    loadConversations,
  };
}