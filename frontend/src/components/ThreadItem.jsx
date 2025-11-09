import { useState } from 'react'
import { Trash2, Edit2, Check, X } from 'lucide-react'

/**
 * ThreadItem component - Displays a single thread in the sidebar
 */
function ThreadItem({ thread, isActive, onClick, onDelete, onRename }) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState(thread.title)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleRename = async () => {
    if (editedTitle.trim() && editedTitle !== thread.title) {
      await onRename(thread.id, editedTitle.trim())
    }
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    setEditedTitle(thread.title)
    setIsEditing(false)
  }

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      await onDelete(thread.id)
    } catch (error) {
      console.error('Error deleting thread:', error)
      setIsDeleting(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`

    return date.toLocaleDateString()
  }

  return (
    <div
      className={`group relative p-3 cursor-pointer border-b border-gray-700 transition-colors ${
        isActive
          ? 'bg-blue-900/30 border-l-4 border-l-blue-500'
          : 'hover:bg-gray-750'
      } ${isDeleting ? 'opacity-50' : ''}`}
      onClick={() => !isEditing && onClick(thread.id)}
    >
      {isEditing ? (
        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
          <input
            type="text"
            value={editedTitle}
            onChange={(e) => setEditedTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleRename()
              if (e.key === 'Escape') handleCancelEdit()
            }}
            className="flex-1 bg-gray-700 text-white px-2 py-1 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoFocus
          />
          <button
            onClick={handleRename}
            className="p-1 text-green-400 hover:text-green-300"
            title="Save"
          >
            <Check size={16} />
          </button>
          <button
            onClick={handleCancelEdit}
            className="p-1 text-red-400 hover:text-red-300"
            title="Cancel"
          >
            <X size={16} />
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-gray-100 truncate">
                {thread.title}
              </h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-gray-500">
                  {formatDate(thread.updated_at)}
                </span>
                {thread.message_count > 0 && (
                  <>
                    <span className="text-xs text-gray-600">•</span>
                    <span className="text-xs text-gray-500">
                      {thread.message_count} {thread.message_count === 1 ? 'msg' : 'msgs'}
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Action buttons - shown on hover */}
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setIsEditing(true)
                }}
                className="p-1 text-gray-400 hover:text-blue-400 rounded"
                title="Rename thread"
              >
                <Edit2 size={14} />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  if (window.confirm('Are you sure you want to delete this thread?')) {
                    handleDelete()
                  }
                }}
                className="p-1 text-gray-400 hover:text-red-400 rounded"
                title="Delete thread"
                disabled={isDeleting}
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ThreadItem
