import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function AnalysisReport({ content }) {
  if (!content) {
    return (
      <div className="content-card" style={{ textAlign: 'center', padding: '60px 32px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Analysis not yet generated. Run the analysis first.</p>
      </div>
    );
  }

  return (
    <div className="content-card">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
