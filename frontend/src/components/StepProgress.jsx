import React from 'react';

const STEPS = [
  { id: 'upload', label: 'Upload', icon: '📄' },
  { id: 'analysis', label: 'Analysis', icon: '🔍' },
  { id: 'skills', label: 'Skill Gaps', icon: '🎯' },
  { id: 'improve', label: 'Resume Fixes', icon: '✏️' },
  { id: 'interview', label: 'Interview', icon: '🎤' },
];

export default function StepProgress({ currentStep, completedSteps, onStepClick }) {
  const currentIdx = STEPS.findIndex(s => s.id === currentStep);

  return (
    <div className="step-progress">
      {STEPS.map((step, idx) => {
        const isActive = step.id === currentStep;
        const isCompleted = completedSteps.includes(step.id);
        const isClickable = isCompleted || idx <= currentIdx;

        let className = 'step-item';
        if (isActive) className += ' step-active';
        else if (isCompleted) className += ' step-completed';
        else className += ' step-disabled';

        return (
          <React.Fragment key={step.id}>
            {idx > 0 && (
              <div className={`step-connector ${
                isCompleted ? 'step-connector-completed' : 
                isActive ? 'step-connector-active' : ''
              }`} />
            )}
            <div
              className={className}
              onClick={() => isClickable && onStepClick(step.id)}
              title={step.label}
            >
              <span className="step-number">
                {isCompleted ? '✓' : idx + 1}
              </span>
              <span className="step-label">{step.label}</span>
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
}
