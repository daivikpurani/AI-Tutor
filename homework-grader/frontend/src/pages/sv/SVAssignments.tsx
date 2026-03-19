import React, { useEffect, useState } from 'react';
import { fetchAssignmentsForStudent } from '../../api';

interface SVAssignmentsProps {
  studentId: number;
  onSelectAssignment: (id: number) => void;
}

export default function SVAssignments({ studentId, onSelectAssignment }: SVAssignmentsProps) {
  const [assignments, setAssignments] = useState<Array<{ id: number; title: string; section_code: string | null; due_date: string | null }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchAssignmentsForStudent(studentId)
      .then((d) => setAssignments(d.assignments ?? []))
      .catch((e) => { setError(e.message); setAssignments([]); })
      .finally(() => setLoading(false));
  }, [studentId]);

  if (loading) return <p>Loading assignments…</p>;
  if (error) return <p className="status-err">{error}</p>;

  return (
    <div className="sv-assignments">
      <h2>My assignments</h2>
      <p>Assignments posted by your professor for your section.</p>

      {assignments.length === 0 ? (
        <p>No assignments yet.</p>
      ) : (
        <ul className="assignment-list">
          {assignments.map((a) => (
            <li key={a.id} className="assignment-card">
              <h3>{a.title}</h3>
              <p className="meta">{a.section_code} · Due {a.due_date ? new Date(a.due_date).toLocaleString() : 'TBA'}</p>
              <button type="button" className="btn" onClick={() => onSelectAssignment(a.id)}>
                View & submit
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
