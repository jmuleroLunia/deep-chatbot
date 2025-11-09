import { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'

function MessageList({ messages, isLoading }) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && (
        <div className="text-center text-gray-500 mt-8">
          <p className="text-lg">Welcome to Deep Agent Chatbot</p>
          <p className="text-sm mt-2">Start a conversation to see the agent in action</p>
        </div>
      )}

      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] rounded-lg p-4 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-100'
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="font-semibold">
                {message.role === 'user' ? 'You' : 'Agent'}
              </span>
              <span className="text-xs opacity-70">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>

            {message.content && (
              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}

            {message.tool_calls && message.tool_calls.length > 0 && (
              <div className="mt-3 space-y-2">
                {message.tool_calls.map((tool, idx) => (
                  <div
                    key={idx}
                    className="bg-gray-800 rounded p-2 text-sm border border-gray-600"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-yellow-400">🔧</span>
                      <span className="font-medium">{tool.name}</span>
                    </div>
                    {tool.args && (
                      <pre className="mt-1 text-xs text-gray-400 overflow-x-auto">
                        {JSON.stringify(tool.args, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <div className="animate-pulse text-blue-400">●</div>
              <span className="text-gray-400">Agent is thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList
