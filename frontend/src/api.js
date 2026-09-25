const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:4000';

/**
 * Fetch all stored documents from the backend (sorted newest first)
 */
export async function getDocuments() {
  const response = await fetch(`${API_BASE}/api/documents`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch documents (${response.status})`);
  }
  return response.json();
}

/**
 * Upload a document (.txt, .md, .json)
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/documents`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed (${response.status})`);
  }

  return response.json();
}

/**
 * Delete a document by ID
 */
export async function deleteDocument(id) {
  const response = await fetch(`${API_BASE}/api/documents/${id}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Delete failed (${response.status})`);
  }

  return response.json();
}

/**
 * Download a document file by ID
 */
export async function downloadDocument(id, filename = 'document') {
  const response = await fetch(`${API_BASE}/api/documents/${id}/download`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Download failed (${response.status})`);
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(downloadUrl);
}

/**
 * Ask a question to the AI assistant using uploaded documents as context
 */
export async function askQuestion(question) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chat query failed (${response.status})`);
  }

  return response.json();
}
