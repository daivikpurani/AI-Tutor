import React, { useEffect, useState } from 'react';
import { fetchAssignment, testSolution, uploadSubmission } from './api';

export default function SVAssignmentDetail({ assignmentId, studentId, onBack }) {
  const [assignment, setAssignment] = useState(null);
  const [file, setFile] = useState(null);
  const [testFeedback, setTestFeedback] = useState(null);
  const [testLoading, setTestLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchAssignment(assignmentId).then(setAssignment).catch(() => setAssignment(null));
  }, [assignmentId]);

  async function handleTest(e) {
    e.preventDefault();
    if (!file) { setError('Choose a PDF first.'); return; }
    setError(null);
    setSuccess(null);
    setTestLoading(true);
    try {
      const res = await testSolution(assignmentId, studentId, file);
      setTestFeedback(res.feedback);
      setSuccess('AI feedback received. Revise and test again, or submit for final grading.');
    } catch (err) {
      setError(err.message || 'Test failed.');
    } finally {
      setTestLoading(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) { setError('Choose a PDF first.'); return; }
    setError(null);
    setSuccess(null);
    setSubmitLoading(true);
    try {
      const preFeedback = testFeedback ? JSON.stringify(testFeedback) : undefined;
      await uploadSubmission(assignmentId, studentId, file, preFeedback);
      setSubmitted(true);
      setSuccess('Submitted successfully. Your professor will review and release the final grade.');
    } catch (err) {
      setError(err.message || 'Submit failed.');
    } finally {
      setSubmitLoading(false);
    }
  }

  if (!assignment) return <p className="g-loading">Loading assignment…</p>;

  return (
    <>
      <div style={{ marginBottom: '16px' }}>
        <button className="g-btn-ghost" onClick={onBack} style={{ fontSize: '13px' }}>
          ← Back to assignments
        </button>
      </div>

      <p className="g-page-title">{assignment.title}</p>
      <p className="g-meta" style={{ marginBottom: '20px' }}>
        {assignment.section_code} · Due{' '}
        {assignment.due_date ? new Date(assignment.due_date).toLocaleString() : 'TBA'} · Max{' '}
        {assignment.max_score} pts
      </p>

      {/* Questions */}
      <div className="g-card">
        <h3>Homework questions</h3>
        {assignment.questions_content ? (
          <div
            className="g-questions-content"
            dangerouslySetInnerHTML={{
              __html: assignment.questions_content.replace(/\n/g, '<br/>'),
            }}
          />
        ) : (
          <p className="g-empty">No questions provided by the professor.</p>
        )}
      </div>

      {/* Upload solution */}
      <div className="g-card">
        <h3>Upload your solution</h3>
        <div className="g-form-row">
          <label>PDF file</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            disabled={submitted}
          />
        </div>

        {error   && <div className="g-status-err">{error}</div>}
        {success && <div className="g-status-ok">{success}</div>}

        {!submitted && (
          <div className="g-btn-row">
            <button
              className="g-btn-ghost"
              onClick={handleTest}
              disabled={!file || testLoading}
            >
              {testLoading ? 'Testing with AI…' : 'Test with AI'}
            </button>
            <button
              className="g-btn"
              onClick={handleSubmit}
              disabled={!file || submitLoading}
            >
              {submitLoading ? 'Submitting…' : 'Submit for grading'}
            </button>
          </div>
        )}
      </div>

      {/* AI feedback */}
      {testFeedback && (
        <div className="g-card">
          <h3>AI feedback {submitted ? '(before submission — for reference)' : ''}</h3>
          {submitted && (
            <p className="g-disclaimer">
              This is not your final grade. Your professor will review and release the actual grade.
            </p>
          )}
          <div className="g-ai-feedback">
            <div className="g-score-pill">
              {testFeedback.score} / {testFeedback.max_score}
            </div>
            {testFeedback.summary    && <p><strong>Summary</strong><br />{testFeedback.summary}</p>}
            {testFeedback.strengths  && <p><strong>Strengths</strong><br />{testFeedback.strengths}</p>}
            {testFeedback.weaknesses && <p><strong>Weaknesses</strong><br />{testFeedback.weaknesses}</p>}
            {testFeedback.suggestions && <p><strong>Suggestions</strong><br />{testFeedback.suggestions}</p>}
          </div>
        </div>
      )}
    </>
  );
}
