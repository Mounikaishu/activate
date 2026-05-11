import React, { useState, useRef } from 'react';

export default function UploadPanel({ onSubmit, isLoading }) {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && isValidFile(file)) setResumeFile(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && isValidFile(file)) setResumeFile(file);
  };

  const isValidFile = (file) => {
    const validTypes = ['.pdf', '.docx', '.txt'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    return validTypes.includes(ext);
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const canSubmit = resumeFile && jdText.trim().length > 20 && !isLoading;

  const handleSubmit = () => {
    if (canSubmit) onSubmit(resumeFile, jdText);
  };

  return (
    <div>
      <div className="upload-panel">
        {/* Resume Upload */}
        <div className="upload-section">
          <h3 className="upload-section-title">📄 Your Resume</h3>
          <p className="upload-section-desc">Upload your resume in PDF, DOCX, or TXT format</p>

          {!resumeFile ? (
            <div
              className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <span className="drop-zone-icon">⬆️</span>
              <p className="drop-zone-text">Drag & drop your resume here</p>
              <p className="drop-zone-hint">or click to browse • PDF, DOCX, TXT</p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
            </div>
          ) : (
            <div className="file-preview">
              <span className="file-preview-icon">📋</span>
              <div className="file-preview-info">
                <p className="file-preview-name">{resumeFile.name}</p>
                <p className="file-preview-size">{formatSize(resumeFile.size)}</p>
              </div>
              <button
                className="file-remove-btn"
                onClick={() => setResumeFile(null)}
                title="Remove file"
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* Job Description */}
        <div className="upload-section">
          <h3 className="upload-section-title">💼 Job Description</h3>
          <p className="upload-section-desc">Paste the full job description for the role you're targeting</p>
          <textarea
            className="jd-textarea"
            placeholder={"Paste the complete job description here...\n\nInclude:\n• Role title and company\n• Required skills and qualifications\n• Responsibilities\n• Preferred experience"}
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </div>
      </div>

      <button
        className="btn-primary"
        onClick={handleSubmit}
        disabled={!canSubmit}
      >
        {isLoading ? (
          <>
            <span className="spinner" style={{ width: 20, height: 20, borderWidth: 2, marginBottom: 0 }} />
            Uploading...
          </>
        ) : (
          <>🔍 Analyze My Resume — Get the Brutal Truth</>
        )}
      </button>
    </div>
  );
}
