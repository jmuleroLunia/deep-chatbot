import { useState, useEffect } from 'react'
import { Plus, RefreshCw, MessageSquare } from 'lucide-react'
import ThreadItem from './ThreadItem'
import { getThreads, createThread, updateThread, deleteThread } from '../utils/api'

/**
 * ThreadSidebar component - Manages and displays conversation threads
 */
function ThreadSidebar({ currentThreadId, onThreadSelect, onThreadCreated }) {
  const [threads, setThreads] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)

  // Fetch threads from API
  const fetchThreads = async () => {
    try {
      setIsLoading(true)
      const data = await getThreads()
      setThreads(data)
    } catch (error) {
      console.error('Error fetching threads:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Create new thread
  const handleCreateThread = async () => {
    try {
      setIsCreating(true)
      const newThread = await createThread()
      setThreads(prev => [newThread, ...prev])

      // Notify parent and select new thread
      onThreadCreated(newThread)
      onThreadSelect(newThread.id)
    } catch (error) {
      console.error('Error creating thread:', error)
    } finally {
      setIsCreating(false)
    }
  }

  // Rename thread
  const handleRenameThread = async (threadId, newTitle) => {
    try {
      const updatedThread = await updateThread(threadId, newTitle)
      setThreads(prev =>
        prev.map(thread =>
          thread.id === threadId ? updatedThread : thread
        )
      )
    } catch (error) {
      console.error('Error renaming thread:', error)
    }
  }

  // Delete thread
  const handleDeleteThread = async (threadId) => {
    try {
      await deleteThread(threadId)
      setThreads(prev => prev.filter(thread => thread.id !== threadId))

      // If deleted thread was active, select first available thread or create new one
      if (threadId === currentThreadId) {
        const remainingThreads = threads.filter(t => t.id !== threadId)
        if (remainingThreads.length > 0) {
          onThreadSelect(remainingThreads[0].id)
        } else {
          // No threads left, create a new one
          handleCreateThread()
        }
      }
    } catch (error) {
      console.error('Error deleting thread:', error)
    }
  }

  // Load threads on mount
  useEffect(() => {
    fetchThreads()
  }, [])

  return (
    <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-100 flex items-center gap-2">
            <MessageSquare size={20} />
            Conversations
          </h2>
          <button
            onClick={fetchThreads}
            disabled={isLoading}
            className="p-1.5 text-gray-400 hover:text-gray-200 rounded transition-colors disabled:opacity-50"
            title="Refresh threads"
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
          </button>
        </div>

        <button
          onClick={handleCreateThread}
          disabled={isCreating}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus size={18} />
          New Conversation
        </button>
      </div>

      {/* Thread List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-gray-500 text-sm">Loading threads...</div>
          </div>
        ) : threads.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 px-4 text-center">
            <MessageSquare size={32} className="text-gray-600 mb-2" />
            <p className="text-gray-500 text-sm">No conversations yet</p>
            <p className="text-gray-600 text-xs mt-1">
              Create a new one to get started
            </p>
          </div>
        ) : (
          threads.map(thread => (
            <ThreadItem
              key={thread.id}
              thread={thread}
              isActive={thread.id === currentThreadId}
              onClick={onThreadSelect}
              onDelete={handleDeleteThread}
              onRename={handleRenameThread}
            />
          ))
        )}
      </div>

      {/* Footer info */}
      <div className="p-3 border-t border-gray-700 text-center">
        <p className="text-xs text-gray-500">
          {threads.length} {threads.length === 1 ? 'conversation' : 'conversations'}
        </p>
      </div>
    </div>
  )
}

export default ThreadSidebar
