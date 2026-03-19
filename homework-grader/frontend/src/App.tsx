import React, { useState } from 'react';
import './index.css';

// PV
import PVMaterials from './pages/pv/PVMaterials';
import PVCreateAssignment from './pages/pv/PVCreateAssignment';
import PVGradeSubmissions from './pages/pv/PVGradeSubmissions';

// SV
import SVAssignments from './pages/sv/SVAssignments';
import SVAssignmentDetail from './pages/sv/SVAssignmentDetail';
import SVMySubmissions from './pages/sv/SVMySubmissions';

type View = 'pv' | 'sv';
type PVPage = 'materials' | 'create-assignment' | 'grade';
type SVPage = 'assignments' | 'assignment-detail' | 'my-submissions';

export default function App() {
  const [view, setView] = useState<View>('pv');
  const [pvPage, setPvPage] = useState<PVPage>('materials');
  const [svPage, setSvPage] = useState<SVPage>('assignments');
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<number | null>(null);
  const [selectedStudentId, setSelectedStudentId] = useState<number>(1);

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Homework Grading</h1>
        <p>SF State CS Department</p>
        <div className="view-switcher">
          <button
            className={view === 'pv' ? 'active' : ''}
            onClick={() => { setView('pv'); setPvPage('materials'); }}
          >
            Professor View
          </button>
          <button
            className={view === 'sv' ? 'active' : ''}
            onClick={() => { setView('sv'); setSvPage('assignments'); setSelectedAssignmentId(null); }}
          >
            Student View
          </button>
        </div>
      </header>

      {view === 'pv' && (
        <>
          <nav className="nav-tabs">
            <button className={pvPage === 'materials' ? 'active' : ''} onClick={() => setPvPage('materials')}>
              Upload Materials
            </button>
            <button className={pvPage === 'create-assignment' ? 'active' : ''} onClick={() => setPvPage('create-assignment')}>
              Create Assignment
            </button>
            <button className={pvPage === 'grade' ? 'active' : ''} onClick={() => setPvPage('grade')}>
              Grade Submissions
            </button>
          </nav>
          <main className="main-content">
            {pvPage === 'materials' && <PVMaterials />}
            {pvPage === 'create-assignment' && <PVCreateAssignment />}
            {pvPage === 'grade' && <PVGradeSubmissions />}
          </main>
        </>
      )}

      {view === 'sv' && (
        <>
          <div className="sv-student-picker">
            <label>Student:</label>
            <select
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(Number(e.target.value))}
            >
              <option value={1}>Student 1 — Alice</option>
              <option value={2}>Student 2 — Bob</option>
              <option value={3}>Student 3 — Carol</option>
            </select>
          </div>
          <nav className="nav-tabs">
            <button
              className={svPage === 'assignments' || svPage === 'assignment-detail' ? 'active' : ''}
              onClick={() => { setSvPage('assignments'); setSelectedAssignmentId(null); }}
            >
              My Assignments
            </button>
            <button
              className={svPage === 'my-submissions' ? 'active' : ''}
              onClick={() => { setSvPage('my-submissions'); setSelectedAssignmentId(null); }}
            >
              My Submissions
            </button>
          </nav>
          <main className="main-content">
            {svPage === 'assignments' && (
              <SVAssignments
                studentId={selectedStudentId}
                onSelectAssignment={(id) => { setSelectedAssignmentId(id); setSvPage('assignment-detail'); }}
              />
            )}
            {svPage === 'assignment-detail' && selectedAssignmentId && (
              <SVAssignmentDetail
                assignmentId={selectedAssignmentId}
                studentId={selectedStudentId}
              />
            )}
            {svPage === 'my-submissions' && (
              <SVMySubmissions studentId={selectedStudentId} />
            )}
          </main>
        </>
      )}
    </div>
  );
}
