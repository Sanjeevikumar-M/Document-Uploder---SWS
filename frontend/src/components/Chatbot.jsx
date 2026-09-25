import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Sparkles, BookOpen, AlertCircle, Loader2 } from 'lucide-react';
import { askQuestion } from '../api';

export default function Chatbot({ documentCount = 0 }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      text: 'Hello! I can answer questions about your uploaded documents. Ask me about policies, project timelines, or document summaries!',
      sources: []
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isAsking]);

  const handleSend = async (questionText) => {
    const q = (questionText || inputQuestion).trim();
    if (!q) {
      setError('Please type a question before sending.');
      return;
    }

    setError(null);
    setInputQuestion('');

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: q
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsAsking(true);

    try {
      const response = await askQuestion(q);
      const botMessage = {
        id: `bot-${Date.now()}`,
        role: 'assistant',
        text: response.answer,
        sources: response.sources || []
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(err.message || 'Failed to get an answer.');
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          role: 'assistant',
          text: `Error: ${err.message || 'Could not retrieve answer from documents.'}`,
          sources: []
        }
      ]);
    } finally {
      setIsAsking(false);
    }
  };

  const sampleQuestions = [
    'What does the expense policy say about meal allowances?',
    'What is the goal of the Orion onboarding revamp?',
    'What are the key features mentioned in welcome.md?'
  ];

  return (
    <div className="card chat-card">
      <div className="card-header justify-between">
        <div className="flex-row items-center gap-2">
          <div className="header-icon-badge bot-badge">
            <Bot size={20} className="text-accent" />
          </div>
          <div>
            <h2>Document Assistant</h2>
            <p className="subtitle">
              Answers grounded in {documentCount} stored {documentCount === 1 ? 'document' : 'documents'}
            </p>
          </div>
        </div>
      </div>

      <div className="chat-messages-container">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-message ${msg.role === 'user' ? 'message-user' : 'message-bot'}`}
          >
            <div className="message-avatar">
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className="message-bubble">
              <div className="message-text">{msg.text}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="message-sources">
                  <div className="sources-label">
                    <BookOpen size={12} className="inline-icon" />
                    <span>Sources:</span>
                  </div>
                  <div className="sources-tags">
                    {msg.sources.map((src, i) => (
                      <span key={src._id || i} className="source-tag">
                        {src.originalName}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isAsking && (
          <div className="chat-message message-bot">
            <div className="message-avatar">
              <Bot size={16} />
            </div>
            <div className="message-bubble message-loading">
              <Loader2 size={16} className="spinner inline-icon" />
              <span>Searching documents and generating answer...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {messages.length <= 2 && (
        <div className="suggested-questions">
          <span className="suggested-title">
            <Sparkles size={14} className="inline-icon" /> Suggested queries:
          </span>
          <div className="suggested-chips">
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                className="chip-btn"
                onClick={() => handleSend(q)}
                disabled={isAsking}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="alert alert-error chat-alert">
          <AlertCircle size={16} className="alert-icon" />
          <span>{error}</span>
        </div>
      )}

      <form
        className="chat-input-form"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about your documents..."
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          disabled={isAsking}
        />
        <button
          type="submit"
          className="btn btn-primary btn-send"
          disabled={!inputQuestion.trim() || isAsking}
          title="Send message"
        >
          {isAsking ? <Loader2 size={18} className="spinner" /> : <Send size={18} />}
        </button>
      </form>
    </div>
  );
}
