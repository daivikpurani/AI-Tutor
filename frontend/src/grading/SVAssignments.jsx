import React, { useEffect, useState } from 'react';
import { fetchAssignmentsForStudent } from './api';

export default function SVAssignments({ studentId, onSelectAssignment }) {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchAssignmentsForStudent(studentId)
      .then(setAssignments)
      .catch((e) => { setError(e.message); setAssignments([]); })
      .finally(() => setLoading(false));
  }, [studentId]);

  if (loading) return <p className="g-loading">Loading assignments…</p>;
  if (error)   return <div className="g-status-err">{error}</div>;

  return (
    <>
      <p className="g-page-title">My assignments</p>
      <p className="g-page-subtitle">
        Assignments posted by your professor. Click an assignment to view questions, test your
        solution with AI, and submit.
      </p>

      {assignments.length === 0 ? (
        <p className="g-empty">No assignments available yet.</p>
      ) : (
        <ul className="g-assignment-list">
          {assignments.map((a) => (
            <li key={a.id} className="g-assignment-card">
              <h3>{a.title}</h3>
              <p className="g-meta">
                {a.section_code} · Due {a.due_date ? new Date(a.due_date).toLocaleString() : 'TBA'}
              </p>
              <div className="g-btn-row">
                <button className="g-btn" onClick={() => onSelectAssignment(a.id)}>
                  View &amp; submit
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
