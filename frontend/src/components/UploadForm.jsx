import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '../api';

export default function UploadForm({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const allowedExtensions = ['.txt', '.md', '.json'];

  const validateFile = (file) => {
    if (!file) return false;
    const name = file.name.toLowerCase();
    const hasValidExt = allowedExtensions.some(ext => name.endsWith(ext));
    if (!hasValidExt) {
      setMessage({ type: 'error', text: 'Supported formats: .txt, .md, .json only.' });
      return false;
    }
    return true;
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
      setMessage(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
      setMessage(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Please select a file to upload.' });
      return;
    }

    setIsUploading(true);
    setMessage(null);

    try {
      const doc = await uploadDocument(selectedFile);
      setMessage({
        type: 'success',
        text: `Uploaded "${doc.originalName}" successfully!`
      });
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to upload document.' });
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  return (
    <div className="card upload-card">
      <div className="card-header">
        <div className="header-icon-badge">
          <Upload size={20} className="text-primary" />
        </div>
        <div>
          <h2>Upload Document</h2>
          <p className="subtitle">Supported formats: .txt, .md, .json</p>
        </div>
      </div>

      <form onSubmit={handleUpload}>
        <div
          className={`dropzone ${isDragOver ? 'drag-over' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".txt,.md,.json"
            style={{ display: 'none' }}
          />

          {selectedFile ? (
            <div className="selected-file-info">
              <FileText size={32} className="file-icon" />
              <div>
                <p className="file-name">{selectedFile.name}</p>
                <p className="file-size">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
          ) : (
            <div className="dropzone-content">
              <Upload size={32} className="dropzone-icon" />
              <p className="dropzone-text">
                <span className="browse-link">Click to browse</span> or drag and drop file here
              </p>
              <span className="dropzone-hint">Maximum file size: 10MB</span>
            </div>
          )}
        </div>

        {message && (
          <div className={`alert alert-${message.type}`}>
            {message.type === 'success' ? (
              <CheckCircle2 size={18} className="alert-icon" />
            ) : (
              <AlertCircle size={18} className="alert-icon" />
            )}
            <span>{message.text}</span>
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary btn-block"
          disabled={!selectedFile || isUploading}
        >
          {isUploading ? (
            <>
              <Loader2 size={18} className="spinner" />
              <span>Uploading & Extracting...</span>
            </>
          ) : (
            <>
              <Upload size={18} />
              <span>Upload Document</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
