import React, { useState } from 'react';
import StepProgress from './components/StepProgress';
import UploadPanel from './components/UploadPanel';
import VerdictCard from './components/VerdictCard';
import AnalysisReport from './components/AnalysisReport';
import SkillGapPanel from './components/SkillGapPanel';
import ImprovementPanel from './components/ImprovementPanel';
import InterviewChat from './components/InterviewChat';
import { uploadDocuments, runAnalysis } from './api';

export default function App() {
  // Workflow state
  const [currentStep, setCurrentStep] = useState('upload');
  const [completedSteps, setCompletedSteps] = useState([]);

  // Session
  const [sessionId, setSessionId] = useState(null);

  // Loading states
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzePhase, setAnalyzePhase] = useState(0);

  // Analysis results
  const [verdict, setVerdict] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [skillGaps, setSkillGaps] = useState(null);
  const [improvements, setImprovements] = useState(null);

  // Error
  const [error, setError] = useState(null);

  // Active tab within analysis view
  const [activeTab, setActiveTab] = useState('analysis');

  const markComplete = (step) => {
    setCompletedSteps(prev => prev.includes(step) ? prev : [...prev, step]);
  };

  // --- Upload Handler ---
  const handleUpload = async (resumeFile, jdText) => {
    setError(null);
    setIsUploading(true);

    try {
      const res = await uploadDocuments(resumeFile, jdText);
      setSessionId(res.session_id);
      markComplete('upload');

      // Immediately start analysis
      setIsAnalyzing(true);
      setCurrentStep('analysis');
      setAnalyzePhase(1);

      const analysisRes = await runAnalysis(res.session_id);

      setVerdict(analysisRes.verdict);
      setAnalysis(analysisRes.analysis);
      setAnalyzePhase(2);

      setSkillGaps(analysisRes.skill_gaps);
      setAnalyzePhase(3);

      setImprovements(analysisRes.improvements);

      markComplete('analysis');
      markComplete('skills');
      markComplete('improve');
      setIsAnalyzing(false);
      setActiveTab('analysis');
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Something went wrong.';
      setError(msg);
      setCurrentStep('upload');
    }

    setIsUploading(false);
    setIsAnalyzing(false);
  };

  // --- Step Navigation ---
  const handleStepClick = (stepId) => {
    if (stepId === 'interview' && !completedSteps.includes('analysis')) return;
    setCurrentStep(stepId);
  };

  // --- Reset ---
  const handleReset = () => {
    setCurrentStep('upload');
    setCompletedSteps([]);
    setSessionId(null);
    setVerdict(null);
    setAnalysis(null);
    setSkillGaps(null);
    setImprovements(null);
    setError(null);
    setActiveTab('analysis');
  };

  // --- Render Content ---
  const renderContent = () => {
    // Loading state
    if (isAnalyzing) {
      return (
        <div className="loading-overlay">
          <div className="spinner" />
          <p className="loading-text">Analyzing your resume...</p>
          <p className="loading-subtext">The AI is reviewing your resume against the job description. This takes 30-60 seconds.</p>
          <div className="loading-steps">
            <div className={`loading-step ${analyzePhase >= 1 ? 'active' : ''} ${analyzePhase > 1 ? 'done' : ''}`}>
              {analyzePhase > 1 ? '✅' : '⏳'} Recruiter verdict & detailed analysis
            </div>
            <div className={`loading-step ${analyzePhase >= 2 ? 'active' : ''} ${analyzePhase > 2 ? 'done' : ''}`}>
              {analyzePhase > 2 ? '✅' : analyzePhase >= 2 ? '⏳' : '⬜'} Skill gap detection & roadmap
            </div>
            <div className={`loading-step ${analyzePhase >= 3 ? 'active' : ''}`}>
              {analyzePhase > 3 ? '✅' : analyzePhase >= 3 ? '⏳' : '⬜'} Resume improvement suggestions
            </div>
          </div>
        </div>
      );
    }

    switch (currentStep) {
      case 'upload':
        return <UploadPanel onSubmit={handleUpload} isLoading={isUploading} />;

      case 'analysis':
        return (
          <div>
            {verdict && <VerdictCard verdict={verdict} />}
            <div className="tab-nav">
              <button
                className={`tab-btn ${activeTab === 'analysis' ? 'tab-active' : ''}`}
                onClick={() => setActiveTab('analysis')}
              >
                🔍 Recruiter Analysis
              </button>
              <button
                className={`tab-btn ${activeTab === 'skills' ? 'tab-active' : ''}`}
                onClick={() => setActiveTab('skills')}
              >
                🎯 Skill Gaps
              </button>
              <button
                className={`tab-btn ${activeTab === 'improve' ? 'tab-active' : ''}`}
                onClick={() => setActiveTab('improve')}
              >
                ✏️ Resume Fixes
              </button>
            </div>
            {activeTab === 'analysis' && <AnalysisReport content={analysis} />}
            {activeTab === 'skills' && <SkillGapPanel content={skillGaps} />}
            {activeTab === 'improve' && <ImprovementPanel content={improvements} />}

            <div style={{ marginTop: 24, display: 'flex', gap: 12, justifyContent: 'center' }}>
              <button className="btn-secondary" onClick={handleReset}>
                ↺ Start Over
              </button>
              <button
                className="btn-primary"
                style={{ maxWidth: 320 }}
                onClick={() => { setCurrentStep('interview'); }}
              >
                🎤 Enter Interview Mode
              </button>
            </div>
          </div>
        );

      case 'skills':
        return (
          <div>
            <SkillGapPanel content={skillGaps} />
            <div style={{ marginTop: 24, textAlign: 'center' }}>
              <button className="btn-secondary" onClick={() => setCurrentStep('analysis')}>
                ← Back to Analysis
              </button>
            </div>
          </div>
        );

      case 'improve':
        return (
          <div>
            <ImprovementPanel content={improvements} />
            <div style={{ marginTop: 24, textAlign: 'center' }}>
              <button className="btn-secondary" onClick={() => setCurrentStep('analysis')}>
                ← Back to Analysis
              </button>
            </div>
          </div>
        );

      case 'interview':
        return <InterviewChat sessionId={sessionId} />;

      default:
        return null;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Placement Reality Check</h1>
        <p className="app-subtitle">
          Brutally honest AI-powered resume analysis. No sugarcoating.
        </p>
      </header>

      <StepProgress
        currentStep={currentStep}
        completedSteps={completedSteps}
        onStepClick={handleStepClick}
      />

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            style={{
              marginLeft: 'auto', background: 'none', border: 'none',
              color: 'var(--color-danger)', cursor: 'pointer', fontSize: '1rem'
            }}
          >
            ✕
          </button>
        </div>
      )}

      {renderContent()}
    </div>
  );
}
