import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function SkillGapPanel({ content }) {
  if (!content) {
    return (
      <div className="content-card" style={{ textAlign: 'center', padding: '60px 32px' }}>
        <p style={{ color: 'var(--text-muted)' }}>Skill gap analysis not yet generated.</p>
      </div>
    );
  }

  return (
    <div className="content-card">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
