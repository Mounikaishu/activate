import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function ImprovementPanel({ content }) {
  if (!content) {
    return (
      <div className="content-card" style={{ textAlign: 'center', padding: '60px 32px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Resume improvements not yet generated.</p>
      </div>
    );
  }

  return (
    <div className="content-card">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
