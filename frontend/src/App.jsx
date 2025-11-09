import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import ThreadSidebar from './components/ThreadSidebar'
import './App.css'

function App() {
  const [currentThreadId, setCurrentThreadId] = useState(null)
  const [shouldLoadMessages, setShouldLoadMessages] = useState(false)

  // Load thread ID from localStorage on mount
  useEffect(() => {
    const savedThreadId = localStorage.getItem('currentThreadId')
    if (savedThreadId) {
      setCurrentThreadId(savedThreadId)
    }
  }, [])

  // Save thread ID to localStorage when it changes
  useEffect(() => {
    if (currentThreadId) {
      localStorage.setItem('currentThreadId', currentThreadId)
    }
  }, [currentThreadId])

  const handleThreadSelect = (threadId) => {
    setCurrentThreadId(threadId)
    setShouldLoadMessages(true)
  }

  const handleThreadCreated = (thread) => {
    // New thread created, don't load messages (empty thread)
    setShouldLoadMessages(false)
  }

  const handleMessagesLoaded = () => {
    setShouldLoadMessages(false)
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="h-screen flex">
        {/* Thread Sidebar */}
        <ThreadSidebar
          currentThreadId={currentThreadId}
          onThreadSelect={handleThreadSelect}
          onThreadCreated={handleThreadCreated}
        />

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          <header className="bg-gray-800 border-b border-gray-700 p-4">
            <h1 className="text-2xl font-bold text-blue-400">Deep Agent Chatbot</h1>
            <p className="text-sm text-gray-400 mt-1">Powered by LangGraph + Ollama</p>
          </header>

          <main className="flex-1 overflow-hidden">
            {currentThreadId ? (
              <ChatInterface
                threadId={currentThreadId}
                shouldLoadMessages={shouldLoadMessages}
                onMessagesLoaded={handleMessagesLoaded}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <h2 className="text-xl text-gray-400 mb-2">Welcome to Deep Agent</h2>
                  <p className="text-gray-500">Select or create a conversation to get started</p>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}

export default App
