import React, { useEffect, useState } from 'react';
import { fetchMySubmissions } from './api';

export default function SVMySubmissions({ studentId }) {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchMySubmissions(studentId)
      .then(setSubmissions)
      .catch((e) => { setError(e.message); setSubmissions([]); })
      .finally(() => setLoading(false));
  }, [studentId]);

  if (loading) return <p className="g-loading">Loading submissions…</p>;
  if (error)   return <div className="g-status-err">{error}</div>;

  return (
    <>
      <p className="g-page-title">My submissions</p>
      <p className="g-page-subtitle">
        All your submitted homework. Once your professor releases a grade you&apos;ll see the score
        and feedback here.
      </p>

      {submissions.length === 0 ? (
        <p className="g-empty">No submissions yet.</p>
      ) : (
        <ul className="g-submission-list">
          {submissions.map((s) => {
            let preFeedback = null;
            if (s.pre_submission_feedback) {
              try { preFeedback = JSON.parse(s.pre_submission_feedback); } catch { /* ignore */ }
            }

            return (
              <li key={s.id} className="g-submission-card">
                <h3>{s.assignment_title || 'Assignment'}</h3>
                <p className="g-meta">
                  {s.section_code} · Submitted {new Date(s.submission_date).toLocaleString()} ·{' '}
                  <span style={{ textTransform: 'capitalize' }}>{s.status}</span>
                </p>
                {s.file_name && (
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    File: {s.file_name}
                  </p>
                )}

                {/* Pre-submission AI feedback */}
                {preFeedback && (
                  <div className="g-ai-feedback" style={{ marginTop: '12px' }}>
                    <h4>AI feedback (before submission)</h4>
                    <div className="g-score-pill">
                      {preFeedback.score} / {preFeedback.max_score ?? 100}
                    </div>
                    {preFeedback.summary && <p>{preFeedback.summary}</p>}
                  </div>
                )}

                {/* Professor released grade */}
                {s.grade_released && (
                  <div className="g-released-grade">
                    <h4>Professor grade (released)</h4>
                    <p>
                      <strong>Score:</strong> {s.score} / {s.max_score}
                    </p>
                    {s.professor_feedback && <p style={{ marginTop: '8px' }}>{s.professor_feedback}</p>}
                  </div>
                )}

                {!s.grade_released && (
                  <p className="g-meta" style={{ marginTop: '12px', fontStyle: 'italic' }}>
                    Awaiting professor review…
                  </p>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
