import React, { useEffect, useState } from 'react';
import { fetchMySubmissions } from '../../api';

interface SVMySubmissionsProps {
  studentId: number;
}

export default function SVMySubmissions({ studentId }: SVMySubmissionsProps) {
  const [submissions, setSubmissions] = useState<Array<{
    id: number;
    assignment_title: string | null;
    section_code: string | null;
    file_name: string | null;
    submission_date: string;
    status: string;
    pre_submission_feedback: string | null;
    grade_released: boolean;
    professor_feedback: string | null;
    score: number | null;
    max_score: number | null;
  }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchMySubmissions(studentId)
      .then((d) => setSubmissions(d.submissions ?? []))
      .catch((e) => { setError(e.message); setSubmissions([]); })
      .finally(() => setLoading(false));
  }, [studentId]);

  if (loading) return <p>Loading…</p>;
  if (error) return <p className="status-err">{error}</p>;

  return (
    <div className="sv-my-submissions">
      <h2>My submissions</h2>
      <p>View your submitted homework and released grades.</p>

      {submissions.length === 0 ? (
        <p>No submissions yet.</p>
      ) : (
        <ul className="submission-list">
          {submissions.map((s) => {
            let preFeedback: { score?: number; max_score?: number; summary?: string } | null = null;
            if (s.pre_submission_feedback) {
              try { preFeedback = JSON.parse(s.pre_submission_feedback); } catch { preFeedback = null; }
            }
            return (
              <li key={s.id} className="submission-card">
                <h3>{s.assignment_title}</h3>
                <p className="meta">{s.section_code} · {new Date(s.submission_date).toLocaleString()} · {s.status}</p>
                {s.file_name && <p><strong>File:</strong> {s.file_name}</p>}

                {preFeedback && (
                  <div className="pre-feedback">
                    <h4>AI feedback (before submit)</h4>
                    <p>Score: {preFeedback.score} / {preFeedback.max_score ?? 100}</p>
                    <p>{preFeedback.summary}</p>
                  </div>
                )}

                {s.grade_released && (
                  <div className="released-grade">
                    <h4>Professor feedback (released)</h4>
                    <p><strong>Score:</strong> {s.score} / {s.max_score}</p>
                    {s.professor_feedback && <p>{s.professor_feedback}</p>}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
