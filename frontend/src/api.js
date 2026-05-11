/**
 * Placement Reality Check — API Client
 */

import axios from 'axios';

// In production (Vercel): set VITE_API_URL to your Render backend URL
// In local dev: Vite proxy handles /api → localhost:8000
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 min timeout — analysis takes multiple LLM calls
});

/**
 * Upload resume + job description, get a session ID back.
 */
export async function uploadDocuments(resumeFile, jdText) {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('jd_text', jdText);

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

/**
 * Run full analysis pipeline (verdict + skill gaps + improvements).
 */
export async function runAnalysis(sessionId) {
  const response = await api.get(`/analyze/${sessionId}`);
  return response.data;
}

/**
 * Get a specific analysis section.
 */
export async function getSection(sessionId, section) {
  const response = await api.get(`/analyze/${sessionId}/section/${section}`);
  return response.data;
}

/**
 * Start mock interview — AI asks the first question.
 */
export async function startInterview(sessionId) {
  const response = await api.post(`/interview/${sessionId}/start`);
  return response.data;
}

/**
 * Send student answer, get AI evaluation + next question.
 */
export async function sendAnswer(sessionId, answer) {
  const response = await api.post(`/interview/${sessionId}/respond`, {
    answer,
  });
  return response.data;
}

/**
 * End interview and get performance summary.
 */
export async function endInterview(sessionId) {
  const response = await api.post(`/interview/${sessionId}/end`);
  return response.data;
}
