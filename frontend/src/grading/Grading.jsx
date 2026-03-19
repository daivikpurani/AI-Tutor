import React, { useState } from 'react';
import './Grading.css';
import PVMaterials from './PVMaterials';
import PVCreateAssignment from './PVCreateAssignment';
import PVGradeSubmissions from './PVGradeSubmissions';
import SVAssignments from './SVAssignments';
import SVAssignmentDetail from './SVAssignmentDetail';
import SVMySubmissions from './SVMySubmissions';

export default function Grading() {
  const [view, setView] = useState('pv');           // 'pv' | 'sv'
  const [pvPage, setPvPage] = useState('materials'); // 'materials' | 'create' | 'grade'
  const [svPage, setSvPage] = useState('assignments'); // 'assignments' | 'detail' | 'submissions'
  const [selectedAssignmentId, setSelectedAssignmentId] = useState(null);
  const [selectedStudentId, setSelectedStudentId] = useState(1);

  function switchView(v) {
    setView(v);
    setPvPage('materials');
    setSvPage('assignments');
    setSelectedAssignmentId(null);
  }

  function goToAssignmentDetail(id) {
    setSelectedAssignmentId(id);
    setSvPage('detail');
  }

  return (
    <div className="grading-page">

      {/* ── View switcher bar ─────────────────────────────────────── */}
      <div className="grading-view-bar">
        <h2>AI Homework Grader</h2>
        <button
          className={`view-btn ${view === 'pv' ? 'active' : ''}`}
          onClick={() => switchView('pv')}
        >
          Professor View
        </button>
        <button
          className={`view-btn ${view === 'sv' ? 'active' : ''}`}
          onClick={() => switchView('sv')}
        >
          Student View
        </button>

        {view === 'sv' && (
          <div className="student-picker">
            <label>Student</label>
            <select
              value={selectedStudentId}
              onChange={(e) => {
                setSelectedStudentId(Number(e.target.value));
                setSvPage('assignments');
                setSelectedAssignmentId(null);
              }}
            >
              <option value={1}>Alice (ID 1)</option>
              <option value={2}>Bob (ID 2)</option>
              <option value={3}>Carol (ID 3)</option>
            </select>
          </div>
        )}
      </div>

      {/* ── Sub-nav ───────────────────────────────────────────────── */}
      {view === 'pv' && (
        <div className="grading-subnav">
          <button
            className={`subnav-btn ${pvPage === 'materials' ? 'active' : ''}`}
            onClick={() => setPvPage('materials')}
          >
            Upload Materials
          </button>
          <button
            className={`subnav-btn ${pvPage === 'create' ? 'active' : ''}`}
            onClick={() => setPvPage('create')}
          >
            Create Assignment
          </button>
          <button
            className={`subnav-btn ${pvPage === 'grade' ? 'active' : ''}`}
            onClick={() => setPvPage('grade')}
          >
            Grade Submissions
          </button>
        </div>
      )}

      {view === 'sv' && (
        <div className="grading-subnav">
          <button
            className={`subnav-btn ${svPage === 'assignments' || svPage === 'detail' ? 'active' : ''}`}
            onClick={() => { setSvPage('assignments'); setSelectedAssignmentId(null); }}
          >
            My Assignments
          </button>
          <button
            className={`subnav-btn ${svPage === 'submissions' ? 'active' : ''}`}
            onClick={() => { setSvPage('submissions'); setSelectedAssignmentId(null); }}
          >
            My Submissions
          </button>
        </div>
      )}

      {/* ── Page content ─────────────────────────────────────────── */}
      <div className="grading-content">
        {view === 'pv' && pvPage === 'materials'  && <PVMaterials />}
        {view === 'pv' && pvPage === 'create'     && <PVCreateAssignment />}
        {view === 'pv' && pvPage === 'grade'      && <PVGradeSubmissions />}

        {view === 'sv' && svPage === 'assignments' && (
          <SVAssignments
            studentId={selectedStudentId}
            onSelectAssignment={goToAssignmentDetail}
          />
        )}
        {view === 'sv' && svPage === 'detail' && selectedAssignmentId && (
          <SVAssignmentDetail
            assignmentId={selectedAssignmentId}
            studentId={selectedStudentId}
            onBack={() => setSvPage('assignments')}
          />
        )}
        {view === 'sv' && svPage === 'submissions' && (
          <SVMySubmissions studentId={selectedStudentId} />
        )}
      </div>

    </div>
  );
}
