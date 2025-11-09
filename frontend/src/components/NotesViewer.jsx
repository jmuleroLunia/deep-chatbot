import { useState } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'

function NotesViewer({ notes, onRefresh }) {
  const [selectedNote, setSelectedNote] = useState(null)

  const selectNote = (note) => {
    setSelectedNote(note)
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
          {notes.map((note) => (
            <button
              key={note.note_id}
              onClick={() => selectNote(note)}
              className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded border border-gray-600 transition-colors"
            >
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span className="text-blue-400">📝</span>
                  <span className="text-sm font-medium truncate">{note.title}</span>
                </div>
                {note.tags && note.tags.length > 0 && (
                  <div className="flex gap-1 ml-6 flex-wrap">
                    {note.tags.map((tag, idx) => (
                      <span key={idx} className="text-xs px-2 py-0.5 bg-blue-900/30 text-blue-300 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="p-4 border-b border-gray-700">
            <button
              onClick={() => setSelectedNote(null)}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              ← Back to list
            </button>
            <h4 className="font-medium mt-2 text-sm">{selectedNote.title}</h4>
            {selectedNote.tags && selectedNote.tags.length > 0 && (
              <div className="flex gap-1 mt-2 flex-wrap">
                {selectedNote.tags.map((tag, idx) => (
                  <span key={idx} className="text-xs px-2 py-0.5 bg-blue-900/30 text-blue-300 rounded">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <pre className="text-xs text-gray-300 whitespace-pre-wrap">
              {selectedNote.content}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

export default NotesViewer
