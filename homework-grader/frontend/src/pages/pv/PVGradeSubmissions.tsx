import React, { useEffect, useState } from 'react';
import {
  fetchSections,
  fetchAssignmentsForSection,
  fetchSubmissionsForAssignment,
  fetchSubmission,
  releaseGrade,
} from '../../api';

export default function PVGradeSubmissions() {
  const [sections, setSections] = useState<{ id: number; section_code: string }[]>([]);
  const [sectionId, setSectionId] = useState('');
  const [assignments, setAssignments] = useState<{ id: number; title: string; submission_count: number }[]>([]);
  const [assignmentId, setAssignmentId] = useState('');
  const [submissions, setSubmissions] = useState<Array<{ id: number; student_name: string; pre_submission_feedback: string | null; has_grade_released: boolean }>>([]);
  const [assignmentTitle, setAssignmentTitle] = useState('');
  const [selectedSubmissionId, setSelectedSubmissionId] = useState<number | null>(null);
  const [submissionDetail, setSubmissionDetail] = useState<{
    student_name: string;
    pre_submission_feedback: string | null;
    grade: { score: number; professor_feedback: string; is_released: boolean } | null;
  } | null>(null);
  const [score, setScore] = useState('');
  const [professorFeedback, setProfessorFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchSections().then((s) => {
      setSections(s);
      if (s.length && !sectionId) setSectionId(String(s[0].id));
    }).catch(() => setSections([]));
  }, []);

  useEffect(() => {
    if (!sectionId) return;
    fetchAssignmentsForSection(Number(sectionId))
      .then((d) => setAssignments(d.assignments ?? []))
      .catch(() => setAssignments([]));
    setAssignmentId('');
    setSubmissions([]);
    setSelectedSubmissionId(null);
  }, [sectionId]);

  useEffect(() => {
    if (!assignmentId) return;
    fetchSubmissionsForAssignment(Number(assignmentId))
      .then((d) => {
        setAssignmentTitle(d.assignment_title);
        setSubmissions(d.submissions ?? []);
      })
      .catch(() => setSubmissions([]));
    setSelectedSubmissionId(null);
  }, [assignmentId]);

  useEffect(() => {
    if (!selectedSubmissionId) {
      setSubmissionDetail(null);
      return;
    }
    fetchSubmission(selectedSubmissionId)
      .then((s) => {
        setSubmissionDetail({
          student_name: s.student_name ?? '',
          pre_submission_feedback: s.pre_submission_feedback,
          grade: s.grade ? { score: s.grade.score, professor_feedback: s.grade.professor_feedback ?? '', is_released: s.grade.is_released } : null,
        });
        setScore(s.grade ? String(s.grade.score) : '');
        setProfessorFeedback(s.grade?.professor_feedback ?? '');
      })
      .catch(() => setSubmissionDetail(null));
  }, [selectedSubmissionId]);

  async function handleRelease(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedSubmissionId || !score.trim()) return;
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      await releaseGrade(selectedSubmissionId, Number(score), professorFeedback.trim() || '');
      setSuccess('Grade released to student.');
      const s = await fetchSubmission(selectedSubmissionId);
      setSubmissionDetail({
        student_name: s.student_name ?? '',
        pre_submission_feedback: s.pre_submission_feedback,
        grade: s.grade ? { score: s.grade.score, professor_feedback: s.grade.professor_feedback ?? '', is_released: true } : null,
      });
      const d = await fetchSubmissionsForAssignment(Number(assignmentId));
      setSubmissions(d.submissions ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed');
    } finally {
      setLoading(false);
    }
  }

  let preFeedback: { score?: number; summary?: string; strengths?: string; weaknesses?: string; suggestions?: string } | null = null;
  if (submissionDetail?.pre_submission_feedback) {
    try {
      preFeedback = JSON.parse(submissionDetail.pre_submission_feedback);
    } catch {
      preFeedback = null;
    }
  }

  return (
    <div className="pv-grade">
      <h2>Grade submissions</h2>
      <p>Select section and assignment, then view each submission. AI feedback (from student&apos;s last test) is shown. Enter score and professor feedback, then release.</p>

      <div className="card">
        <div className="form-row">
          <label>Section</label>
          <select value={sectionId} onChange={(e) => setSectionId(e.target.value)}>
            <option value="">Select section</option>
            {sections.map((s) => (
              <option key={s.id} value={s.id}>{s.section_code}</option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <label>Assignment</label>
          <select value={assignmentId} onChange={(e) => setAssignmentId(e.target.value)}>
            <option value="">Select assignment</option>
            {assignments.map((a) => (
              <option key={a.id} value={a.id}>{a.title} ({a.submission_count} submissions)</option>
            ))}
          </select>
        </div>
      </div>

      {assignmentTitle && (
        <div className="card">
          <h3>{assignmentTitle}</h3>
          {submissions.length === 0 ? (
            <p>No submissions yet.</p>
          ) : (
            <ul className="list">
              {submissions.map((s) => (
                <li key={s.id}>
                  <button
                    type="button"
                    className={selectedSubmissionId === s.id ? 'active' : ''}
                    onClick={() => setSelectedSubmissionId(s.id)}
                  >
                    {s.student_name} {s.has_grade_released ? '✓ Released' : ''}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {submissionDetail && selectedSubmissionId && (
        <div className="card submission-detail">
          <h3>Submission — {submissionDetail.student_name}</h3>

          {preFeedback && (
            <div className="ai-feedback">
              <h4>AI feedback (from student&apos;s last test)</h4>
              <p><strong>Score:</strong> {preFeedback.score} / 100</p>
              <p><strong>Summary:</strong> {preFeedback.summary}</p>
              {preFeedback.strengths && <p><strong>Strengths:</strong> {preFeedback.strengths}</p>}
              {preFeedback.weaknesses && <p><strong>Weaknesses:</strong> {preFeedback.weaknesses}</p>}
              {preFeedback.suggestions && <p><strong>Suggestions:</strong> {preFeedback.suggestions}</p>}
            </div>
          )}

          <form onSubmit={handleRelease}>
            <div className="form-row">
              <label>Score</label>
              <input type="number" min={0} step={0.5} value={score} onChange={(e) => setScore(e.target.value)} required />
            </div>
            <div className="form-row">
              <label>Professor feedback (sent to student)</label>
              <textarea value={professorFeedback} onChange={(e) => setProfessorFeedback(e.target.value)} rows={4} placeholder="Your feedback to the student" />
            </div>
            {error && <p className="status-err">{error}</p>}
            {success && <p className="status-ok">{success}</p>}
            <button type="submit" className="btn" disabled={loading || submissionDetail.grade?.is_released}>
              {submissionDetail.grade?.is_released ? 'Already released' : loading ? 'Releasing…' : 'Release grade to student'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
