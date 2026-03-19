import React, { useEffect, useState } from 'react';
import {
  fetchAssignment,
  fetchSubmissionsForAssignment,
  testSolution,
  uploadSubmission,
} from '../../api';

interface SVAssignmentDetailProps {
  assignmentId: number;
  studentId: number;
}

export default function SVAssignmentDetail({ assignmentId, studentId }: SVAssignmentDetailProps) {
  const [assignment, setAssignment] = useState<{
    title: string;
    questions_content: string | null;
    section_code: string | null;
    due_date: string | null;
    max_score: number;
  } | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [lastTestFeedback, setLastTestFeedback] = useState<{
    score: number;
    max_score: number;
    summary: string;
    strengths: string;
    weaknesses: string;
    suggestions: string;
  } | null>(null);
  const [testLoading, setTestLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    fetchAssignment(assignmentId).then(setAssignment).catch(() => setAssignment(null));
  }, [assignmentId]);

  async function handleTest(e: React.FormEvent) {
    e.preventDefault();
    if (!file) { setError('Choose a PDF first.'); return; }
    setError(null);
    setSuccess(null);
    setTestLoading(true);
    try {
      const res = await testSolution(assignmentId, studentId, file);
      setLastTestFeedback(res.feedback);
      setSuccess('AI feedback received. You can revise and test again, or submit.');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Test failed');
    } finally {
      setTestLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) { setError('Choose a PDF first.'); return; }
    setError(null);
    setSuccess(null);
    setSubmitLoading(true);
    try {
      const preFeedback = lastTestFeedback ? JSON.stringify(lastTestFeedback) : undefined;
      await uploadSubmission(assignmentId, studentId, file, preFeedback);
      setSubmitted(true);
      setSuccess('Submitted. Your last test feedback is below for reference. Final grade will be released by your professor.');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Submit failed');
    } finally {
      setSubmitLoading(false);
    }
  }

  if (!assignment) return <p>Loading…</p>;

  return (
    <div className="sv-assignment-detail">
      <h2>{assignment.title}</h2>
      <p className="meta">{assignment.section_code} · Due {assignment.due_date ? new Date(assignment.due_date).toLocaleString() : 'TBA'} · Max {assignment.max_score} pts</p>

      <div className="card questions-card">
        <h3>Homework questions</h3>
        {assignment.questions_content ? (
          <div className="questions-content" dangerouslySetInnerHTML={{ __html: assignment.questions_content.replace(/\n/g, '<br/>') }} />
        ) : (
          <p>No questions provided.</p>
        )}
      </div>

      <div className="card">
        <h3>Upload solution</h3>
        <form>
          <div className="form-row">
            <label>PDF file</label>
            <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0] ?? null)} disabled={submitted} />
          </div>
          {!submitted && (
            <div className="button-row">
              <button type="button" className="btn btn-secondary" onClick={handleTest} disabled={!file || testLoading}>
                {testLoading ? 'Testing…' : 'Test with AI'}
              </button>
              <button type="button" className="btn" onClick={handleSubmit} disabled={!file || submitLoading}>
                {submitLoading ? 'Submitting…' : 'Submit for professor'}
              </button>
            </div>
          )}
        </form>
        {error && <p className="status-err">{error}</p>}
        {success && <p className="status-ok">{success}</p>}
      </div>

      {lastTestFeedback && (
        <div className="card feedback-card">
          <h3>AI feedback {submitted ? '(before submission — for your reference)' : ''}</h3>
          {submitted && (
            <p className="disclaimer">This is not the final grade. Your professor will review and release the actual grade.</p>
          )}
          <p><strong>Score:</strong> {lastTestFeedback.score} / {lastTestFeedback.max_score}</p>
          <p><strong>Summary:</strong> {lastTestFeedback.summary}</p>
          {lastTestFeedback.strengths && <p><strong>Strengths:</strong> {lastTestFeedback.strengths}</p>}
          {lastTestFeedback.weaknesses && <p><strong>Weaknesses:</strong> {lastTestFeedback.weaknesses}</p>}
          {lastTestFeedback.suggestions && <p><strong>Suggestions:</strong> {lastTestFeedback.suggestions}</p>}
        </div>
      )}
    </div>
  );
}
