import React, { useEffect, useState } from 'react';
import {
  fetchSections,
  fetchAssignmentsForSection,
  fetchSubmissionsForAssignment,
  fetchSubmission,
  releaseGrade,
} from './api';

export default function PVGradeSubmissions() {
  const [sections, setSections] = useState([]);
  const [sectionId, setSectionId] = useState('');
  const [assignments, setAssignments] = useState([]);
  const [assignmentId, setAssignmentId] = useState('');
  const [assignmentTitle, setAssignmentTitle] = useState('');
  const [submissions, setSubmissions] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [score, setScore] = useState('');
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchSections()
      .then((s) => { setSections(s); if (s.length) setSectionId(String(s[0].id)); })
      .catch(() => setSections([]));
  }, []);

  useEffect(() => {
    if (!sectionId) return;
    fetchAssignmentsForSection(Number(sectionId))
      .then(setAssignments)
      .catch(() => setAssignments([]));
    setAssignmentId('');
    setSubmissions([]);
    setSelectedId(null);
  }, [sectionId]);

  useEffect(() => {
    if (!assignmentId) return;
    fetchSubmissionsForAssignment(Number(assignmentId))
      .then((d) => { setAssignmentTitle(d.assignment_title); setSubmissions(d.submissions); })
      .catch(() => setSubmissions([]));
    setSelectedId(null);
  }, [assignmentId]);

  useEffect(() => {
    if (!selectedId) { setDetail(null); return; }
    fetchSubmission(selectedId).then((s) => {
      setDetail(s);
      setScore(s.grade ? String(s.grade.score) : '');
      setFeedback(s.grade?.professor_feedback ?? '');
    }).catch(() => setDetail(null));
  }, [selectedId]);

  async function handleRelease(e) {
    e.preventDefault();
    if (!selectedId || !score) return;
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      await releaseGrade(selectedId, Number(score), feedback);
      setSuccess('Grade released to student.');
      const s = await fetchSubmission(selectedId);
      setDetail(s);
      const d = await fetchSubmissionsForAssignment(Number(assignmentId));
      setSubmissions(d.submissions);
    } catch (err) {
      setError(err.message || 'Release failed.');
    } finally {
      setLoading(false);
    }
  }

  // Parse JSON pre-submission AI feedback
  let preFeedback = null;
  if (detail?.pre_submission_feedback) {
    try { preFeedback = JSON.parse(detail.pre_submission_feedback); } catch { /* ignore */ }
  }

  return (
    <>
      <p className="g-page-title">Grade submissions</p>
      <p className="g-page-subtitle">
        Select a section and assignment, then pick a submission. AI feedback from the student&apos;s
        last test run is shown. Enter the final score, add your notes, and release to the student.
      </p>

      {/* Section + Assignment selectors */}
      <div className="g-card">
        <div className="g-form-row">
          <label>Section</label>
          <select value={sectionId} onChange={(e) => setSectionId(e.target.value)}>
            <option value="">Select section…</option>
            {sections.map((s) => (
              <option key={s.id} value={s.id}>{s.section_code}</option>
            ))}
          </select>
        </div>
        <div className="g-form-row" style={{ marginBottom: 0 }}>
          <label>Assignment</label>
          <select value={assignmentId} onChange={(e) => setAssignmentId(e.target.value)}>
            <option value="">Select assignment…</option>
            {assignments.map((a) => (
              <option key={a.id} value={a.id}>
                {a.title} ({a.submission_count} submission{a.submission_count !== 1 ? 's' : ''})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Submission list */}
      {assignmentTitle && (
        <div className="g-card">
          <h3>{assignmentTitle}</h3>
          {submissions.length === 0 ? (
            <p className="g-empty">No submissions yet.</p>
          ) : (
            <ul className="g-list" style={{ gap: '8px' }}>
              {submissions.map((s) => (
                <li key={s.id} style={{ padding: 0, background: 'transparent', border: 'none' }}>
                  <button
                    className={`g-sub-btn ${selectedId === s.id ? 'active' : ''}`}
                    onClick={() => setSelectedId(s.id)}
                  >
                    <span>{s.student_name}</span>
                    {s.has_grade_released && (
                      <span className="g-released-badge">Released</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Submission detail + grade form */}
      {detail && selectedId && (
        <div className="g-card">
          <h3>Submission — {detail.student_name}</h3>

          {/* AI pre-submission feedback */}
          {preFeedback && (
            <div className="g-ai-feedback">
              <h4>AI feedback (student&apos;s last test)</h4>
              <div className="g-score-pill">{preFeedback.score ?? '—'} / 100</div>
              {preFeedback.summary    && <p><strong>Summary</strong><br />{preFeedback.summary}</p>}
              {preFeedback.strengths  && <p><strong>Strengths</strong><br />{preFeedback.strengths}</p>}
              {preFeedback.weaknesses && <p><strong>Weaknesses</strong><br />{preFeedback.weaknesses}</p>}
              {preFeedback.suggestions && <p><strong>Suggestions</strong><br />{preFeedback.suggestions}</p>}
            </div>
          )}

          {!preFeedback && (
            <p className="g-meta" style={{ marginBottom: '16px' }}>
              No pre-submission AI test feedback available.
            </p>
          )}

          {/* Release form */}
          <form onSubmit={handleRelease}>
            <div className="g-form-row">
              <label>Final score</label>
              <input
                type="number"
                min={0}
                step={0.5}
                value={score}
                onChange={(e) => setScore(e.target.value)}
                placeholder="Enter score…"
                required
              />
            </div>
            <div className="g-form-row">
              <label>Professor feedback (sent to student)</label>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                rows={4}
                placeholder="Your written feedback for the student…"
              />
            </div>

            {error   && <div className="g-status-err">{error}</div>}
            {success && <div className="g-status-ok">{success}</div>}

            <div className="g-btn-row">
              <button
                type="submit"
                className="g-btn"
                disabled={loading || detail.grade?.is_released}
              >
                {detail.grade?.is_released
                  ? 'Grade already released'
                  : loading
                  ? 'Releasing…'
                  : 'Release grade to student'}
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
