import React from 'react';

export default function VerdictCard({ verdict }) {
  const isShortlisted = verdict.toUpperCase().includes('SHORTLISTED');
  const className = `verdict-card ${isShortlisted ? 'shortlisted' : 'rejected'}`;

  return (
    <div className={className}>
      <span className="verdict-icon">{isShortlisted ? '✅' : '❌'}</span>
      <h2 className="verdict-label">{verdict}</h2>
      <p className="verdict-reason">
        {isShortlisted
          ? 'Based on the job requirements, your profile has a reasonable chance of passing initial screening. But don\'t get comfortable — read the full analysis below.'
          : 'Based on the job requirements, your resume would likely not survive initial screening. The detailed analysis below explains exactly why and what to fix.'}
      </p>
    </div>
  );
}
