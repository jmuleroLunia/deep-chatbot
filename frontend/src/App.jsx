import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="container mx-auto h-screen flex flex-col">
        <header className="bg-gray-800 border-b border-gray-700 p-4">
          <h1 className="text-2xl font-bold text-blue-400">Deep Agent Chatbot</h1>
          <p className="text-sm text-gray-400 mt-1">Powered by LangGraph + Ollama</p>
        </header>

        <main className="flex-1 overflow-hidden">
          <ChatInterface />
        </main>
      </div>
    </div>
  )
}

export default App
