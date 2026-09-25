import React, { useState, useEffect, useCallback } from 'react';
import { Files, ExternalLink, RefreshCw } from 'lucide-react';
import UploadForm from './components/UploadForm';
import DocumentList from './components/DocumentList';
import Chatbot from './components/Chatbot';
import { getDocuments } from './api';

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      setError(err.message || 'Failed to load documents.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocs();
  }, [fetchDocs]);

  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <header className="navbar">
        <div className="nav-brand">
          <div className="brand-logo">
            <Files size={22} className="logo-icon" />
          </div>
          <div>
            <h1 className="brand-title">Document Uploader</h1>
            <p className="brand-badge">FastAPI + MongoDB Atlas + React</p>
          </div>
        </div>

        <div className="nav-actions">
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={fetchDocs}
            disabled={isLoading}
            title="Refresh document list"
          >
            <RefreshCw size={15} className={isLoading ? 'spinner' : ''} />
            <span>Refresh</span>
          </button>

          <a
            href="http://localhost:4000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline btn-sm"
            title="Open Swagger API documentation"
          >
            <ExternalLink size={15} />
            <span>Swagger Docs</span>
          </a>
        </div>
      </header>

      {/* Main Content Dashboard */}
      <main className="main-content">
        <div className="dashboard-grid">
          {/* Left Column: Upload Form & Document Management */}
          <section className="dashboard-column left-column">
            <UploadForm onUploadSuccess={fetchDocs} />
            <DocumentList
              documents={documents}
              isLoading={isLoading}
              error={error}
              onDocumentDeleted={fetchDocs}
            />
          </section>

          {/* Right Column: AI Document Assistant */}
          <section className="dashboard-column right-column">
            <Chatbot documentCount={documents.length} />
          </section>
        </div>
      </main>

      <footer className="footer">
        <p>Document Uploader & AI Assistant &bull; Single Window Services (SWS)</p>
      </footer>
    </div>
  );
}
