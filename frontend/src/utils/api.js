/**
 * API utility functions for thread management
 */

const API_BASE_URL = 'http://127.0.0.1:8000'

/**
 * Create a new thread
 * @param {string} title - Optional title for the thread
 * @returns {Promise<Object>} The created thread
 */
export async function createThread(title = null) {
  const response = await fetch(`${API_BASE_URL}/api/v1/conversations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  })

  if (!response.ok) {
    throw new Error('Failed to create thread')
  }

  return response.json()
}

/**
 * Get all threads
 * @returns {Promise<Array>} List of threads
 */
export async function getThreads() {
  const response = await fetch(`${API_BASE_URL}/api/v1/conversations`)

  if (!response.ok) {
    throw new Error('Failed to fetch threads')
  }

  const data = await response.json()
  return data.threads || []
}

/**
 * Get a specific thread with its messages
 * @param {string} threadId - The thread ID
 * @returns {Promise<Object>} The thread with messages
 */
export async function getThread(threadId) {
  const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${threadId}/messages`)

  if (!response.ok) {
    throw new Error('Failed to fetch thread')
  }

  return response.json()
}

/**
 * Update a thread's title
 * @param {string} threadId - The thread ID
 * @param {string} title - New title
 * @returns {Promise<Object>} The updated thread
 */
export async function updateThread(threadId, title) {
  const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${threadId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title }),
  })

  if (!response.ok) {
    throw new Error('Failed to update thread')
  }

  return response.json()
}

/**
 * Delete a thread
 * @param {string} threadId - The thread ID
 * @returns {Promise<Object>} Success message
 */
export async function deleteThread(threadId) {
  const response = await fetch(`${API_BASE_URL}/api/v1/conversations/${threadId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error('Failed to delete thread')
  }

  return response.json()
}
