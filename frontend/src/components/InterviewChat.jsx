import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { startInterview, sendAnswer, endInterview } from '../api';

export default function InterviewChat({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [ended, setEnded] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => { scrollToBottom(); }, [messages]);

  const handleStart = async () => {
    setIsLoading(true);
    try {
      const res = await startInterview(sessionId);
      setMessages([{ role: 'ai', content: res.message }]);
      setStarted(true);
    } catch (err) {
      setMessages([{ role: 'ai', content: '⚠️ Failed to start interview. Please try again.' }]);
    }
    setIsLoading(false);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const res = await sendAnswer(sessionId, userMsg);
      setMessages(prev => [...prev, { role: 'ai', content: res.message }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'ai',
        content: '⚠️ Failed to get response. Try again.',
      }]);
    }
    setIsLoading(false);
  };

  const handleEnd = async () => {
    setIsLoading(true);
    try {
      const res = await endInterview(sessionId);
      setMessages(prev => [...prev, {
        role: 'ai',
        content: `## 📋 Interview Performance Summary\n\n${res.summary}`,
      }]);
      setEnded(true);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'ai',
        content: '⚠️ Failed to generate summary.',
      }]);
    }
    setIsLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!started) {
    return (
      <div className="interview-container">
        <div className="interview-start">
          <span className="interview-start-icon">🎤</span>
          <h2>Mock Interview Mode</h2>
          <p>
            The AI will interview you based on your resume claims and the job description.
            Expect tough, probing questions — just like a real technical interview.
            Answer honestly. Weak answers will get follow-ups.
          </p>
          <button
            className="btn-primary"
            onClick={handleStart}
            disabled={isLoading}
            style={{ maxWidth: 320 }}
          >
            {isLoading ? 'Setting up interview...' : '🎬 Start Interview'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="interview-container">
      <div className="interview-header">
        <span className="interview-title">🎤 Mock Interview in Progress</span>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {!ended && <span className="interview-badge live">● LIVE</span>}
          {!ended && (
            <button className="btn-danger" onClick={handleEnd} disabled={isLoading}>
              End Interview
            </button>
          )}
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.role === 'ai' ? 'ai' : 'user'}`}>
            <span className="chat-bubble-label">
              {msg.role === 'ai' ? '🎯 Interviewer' : '👤 You'}
            </span>
            {msg.role === 'ai' ? (
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            ) : (
              <p>{msg.content}</p>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="chat-bubble ai">
            <span className="chat-bubble-label">🎯 Interviewer</span>
            <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Thinking...</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {!ended && (
        <div className="chat-input-area">
          <input
            className="chat-input"
            type="text"
            placeholder="Type your answer..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            className="chat-send-btn"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
          >
            Send
          </button>
        </div>
      )}

      {ended && (
        <div className="chat-input-area" style={{ justifyContent: 'center' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Interview ended. Review the performance summary above.
          </p>
        </div>
      )}
    </div>
  );
}
