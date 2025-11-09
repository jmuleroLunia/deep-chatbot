import { useState, useEffect } from 'react'
import axios from 'axios'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import PlanViewer from './PlanViewer'
import NotesViewer from './NotesViewer'
import { getThread } from '../utils/api'

const API_BASE_URL = 'http://127.0.0.1:8000'

function ChatInterface({ threadId, shouldLoadMessages, onMessagesLoaded }) {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [showPlan, setShowPlan] = useState(false)
  const [showNotes, setShowNotes] = useState(false)
  const [plan, setPlan] = useState(null)
  const [notes, setNotes] = useState([])

  // Load messages from thread when switching threads
  useEffect(() => {
    if (shouldLoadMessages && threadId) {
      loadThreadMessages()
    }
  }, [shouldLoadMessages, threadId])

  // Clear messages when thread changes
  useEffect(() => {
    if (threadId) {
      setMessages([])
      loadThreadMessages()
    }
  }, [threadId])

  // Load thread messages from backend
  const loadThreadMessages = async () => {
    try {
      const threadData = await getThread(threadId)
      // Convert backend message format to frontend format
      const formattedMessages = threadData.messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
        tool_calls: msg.tool_calls || []
      }))
      setMessages(formattedMessages)
      if (onMessagesLoaded) {
        onMessagesLoaded()
      }
    } catch (error) {
      console.error('Error loading thread messages:', error)
      setMessages([])
    }
  }

  // Fetch plan
  const fetchPlan = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/plan`)
      setPlan(response.data)
    } catch (error) {
      console.error('Error fetching plan:', error)
      setPlan(null)
    }
  }

  // Fetch notes
  const fetchNotes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/notes`)
      setNotes(response.data.notes || [])
    } catch (error) {
      console.error('Error fetching notes:', error)
      setNotes([])
    }
  }

  // Send message with streaming
  const sendMessage = async (messageText) => {
    // Add user message
    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Use streaming endpoint
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText,
          thread_id: threadId
        })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let assistantMessage = {
        role: 'assistant',
        content: '',
        tool_calls: [],
        timestamp: new Date().toISOString()
      }

      // Add empty assistant message that we'll update
      setMessages(prev => [...prev, assistantMessage])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue

            try {
              const parsed = JSON.parse(data)

              if (parsed.type === 'token') {
                // Update assistant message content
                assistantMessage.content += parsed.content
                setMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1] = { ...assistantMessage }
                  return newMessages
                })
              } else if (parsed.type === 'tool_call') {
                // Add tool call
                assistantMessage.tool_calls.push(parsed)
                setMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1] = { ...assistantMessage }
                  return newMessages
                })
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }

      // Refresh plan and notes after message
      fetchPlan()
      fetchNotes()

    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Error: Could not connect to the backend. Make sure the server is running.',
        timestamp: new Date().toISOString()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // Load initial plan and notes
  useEffect(() => {
    fetchPlan()
    fetchNotes()
  }, [])

  return (
    <div className="flex h-full">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        <MessageList messages={messages} isLoading={isLoading} />
        <MessageInput onSend={sendMessage} disabled={isLoading} />
      </div>

      {/* Sidebar */}
      <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
        <div className="flex border-b border-gray-700">
          <button
            onClick={() => { setShowPlan(true); setShowNotes(false); }}
            className={`flex-1 p-3 ${showPlan ? 'bg-gray-700 text-blue-400' : 'text-gray-400 hover:bg-gray-750'}`}
          >
            Plan
          </button>
          <button
            onClick={() => { setShowNotes(true); setShowPlan(false); }}
            className={`flex-1 p-3 ${showNotes ? 'bg-gray-700 text-blue-400' : 'text-gray-400 hover:bg-gray-750'}`}
          >
            Notes
          </button>
        </div>

        <div className="flex-1 overflow-hidden">
          {showPlan && <PlanViewer plan={plan} onRefresh={fetchPlan} />}
          {showNotes && <NotesViewer notes={notes} onRefresh={fetchNotes} />}
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
