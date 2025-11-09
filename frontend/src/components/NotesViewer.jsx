import { useState } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'

function NotesViewer({ notes, onRefresh }) {
  const [selectedNote, setSelectedNote] = useState(null)
  const [noteContent, setNoteContent] = useState('')
  const [loading, setLoading] = useState(false)

  const loadNoteContent = async (filename) => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE_URL}/notes/${filename}`)
      setNoteContent(response.data.content)
      setSelectedNote(filename)
    } catch (error) {
      console.error('Error loading note:', error)
      setNoteContent('Error loading note content')
    } finally {
      setLoading(false)
    }
  }

  if (!notes || notes.length === 0) {
    return (
      <div className="p-4 text-gray-400 text-sm">
        <p>No notes saved yet</p>
        <button
          onClick={onRefresh}
          className="mt-2 text-blue-400 hover:text-blue-300"
        >
          Refresh
        </button>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <h3 className="font-semibold">Notes ({notes.length})</h3>
        <button
          onClick={onRefresh}
          className="text-blue-400 hover:text-blue-300 text-sm"
        >
          Refresh
        </button>
      </div>

      {!selectedNote ? (
        <div className="overflow-y-auto p-4 space-y-2">
          {notes.map((note, index) => (
            <button
              key={index}
              onClick={() => loadNoteContent(note)}
              className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded border border-gray-600 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-blue-400">📝</span>
                <span className="text-sm truncate">{note}</span>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="p-4 border-b border-gray-700">
            <button
              onClick={() => {
                setSelectedNote(null)
                setNoteContent('')
              }}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              ← Back to list
            </button>
            <h4 className="font-medium mt-2 text-sm truncate">{selectedNote}</h4>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <p className="text-gray-400 text-sm">Loading...</p>
            ) : (
              <pre className="text-xs text-gray-300 whitespace-pre-wrap">
                {noteContent}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default NotesViewer
