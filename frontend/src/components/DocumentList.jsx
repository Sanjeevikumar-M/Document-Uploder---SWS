import React, { useState } from 'react';
import { FileText, Download, Trash2, Eye, EyeOff, Loader2, Calendar, HardDrive } from 'lucide-react';
import { deleteDocument, downloadDocument } from '../api';

export default function DocumentList({ documents, isLoading, error, onDocumentDeleted }) {
  const [deletingId, setDeletingId] = useState(null);
  const [previewId, setPreviewId] = useState(null);
  const [actionError, setActionError] = useState(null);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    setDeletingId(id);
    setActionError(null);
    try {
      await deleteDocument(id);
      if (onDocumentDeleted) onDocumentDeleted();
    } catch (err) {
      setActionError(err.message || 'Failed to delete document.');
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownload = async (id, name) => {
    try {
      await downloadDocument(id, name);
    } catch (err) {
      setActionError(err.message || 'Failed to download document.');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const formatDate = (isoString) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoString;
    }
  };

  const getFormatBadge = (filename) => {
    const ext = filename?.split('.').pop()?.toUpperCase() || 'FILE';
    let badgeClass = 'badge-default';
    if (ext === 'TXT') badgeClass = 'badge-txt';
    if (ext === 'MD') badgeClass = 'badge-md';
    if (ext === 'JSON') badgeClass = 'badge-json';
    return <span className={`badge ${badgeClass}`}>{ext}</span>;
  };

  return (
    <div className="card documents-card">
      <div className="card-header justify-between">
        <div className="flex-row items-center gap-2">
          <div className="header-icon-badge">
            <FileText size={20} className="text-primary" />
          </div>
          <div>
            <h2>Stored Documents</h2>
            <p className="subtitle">
              {documents.length} {documents.length === 1 ? 'document' : 'documents'} available
            </p>
          </div>
        </div>
      </div>

      {actionError && (
        <div className="alert alert-error">
          <span>{actionError}</span>
        </div>
      )}

      {isLoading ? (
        <div className="loading-state">
          <Loader2 size={32} className="spinner text-primary" />
          <p>Loading documents...</p>
        </div>
      ) : error ? (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      ) : documents.length === 0 ? (
        <div className="empty-state">
          <FileText size={48} className="empty-icon" />
          <p className="empty-title">No documents uploaded yet</p>
          <p className="empty-subtitle">Upload your first .txt, .md, or .json file to get started.</p>
        </div>
      ) : (
        <div className="documents-table-wrapper">
          <table className="documents-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Type</th>
                <th>Size</th>
                <th>Uploaded</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => {
                const isPreviewing = previewId === doc._id;
                const isDeleting = deletingId === doc._id;

                return (
                  <React.Fragment key={doc._id}>
                    <tr className={isPreviewing ? 'row-expanded' : ''}>
                      <td>
                        <div className="doc-name-cell">
                          <FileText size={18} className="text-secondary" />
                          <span className="doc-title" title={doc.originalName}>
                            {doc.originalName}
                          </span>
                        </div>
                      </td>
                      <td>{getFormatBadge(doc.originalName)}</td>
                      <td>
                        <span className="meta-text">
                          <HardDrive size={13} className="inline-icon" />
                          {formatFileSize(doc.size)}
                        </span>
                      </td>
                      <td>
                        <span className="meta-text">
                          <Calendar size={13} className="inline-icon" />
                          {formatDate(doc.createdAt)}
                        </span>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            type="button"
                            className="btn-icon"
                            title={isPreviewing ? "Hide text" : "Preview text"}
                            onClick={() => setPreviewId(isPreviewing ? null : doc._id)}
                          >
                            {isPreviewing ? <EyeOff size={16} /> : <Eye size={16} />}
                          </button>
                          <button
                            type="button"
                            className="btn-icon"
                            title="Download file"
                            onClick={() => handleDownload(doc._id, doc.originalName)}
                          >
                            <Download size={16} />
                          </button>
                          <button
                            type="button"
                            className="btn-icon btn-danger"
                            title="Delete document"
                            disabled={isDeleting}
                            onClick={() => handleDelete(doc._id, doc.originalName)}
                          >
                            {isDeleting ? <Loader2 size={16} className="spinner" /> : <Trash2 size={16} />}
                          </button>
                        </div>
                      </td>
                    </tr>
                    {isPreviewing && (
                      <tr className="preview-row">
                        <td colSpan={5}>
                          <div className="preview-container">
                            <div className="preview-header">
                              <span>Extracted Text Preview:</span>
                              <span className="char-count">{doc.text?.length || 0} characters</span>
                            </div>
                            <pre className="preview-content">{doc.text || '(No text content extracted)'}</pre>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
