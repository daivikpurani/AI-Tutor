/**
 * Grading API client — calls the homework-grader subsystem at /grading/api/v1/
 * Vite proxies /grading → http://localhost:8000 so no CORS issues.
 */
const BASE = '/grading/api/v1';

async function req(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || res.statusText);
  }
  return res.json();
}

// ── Lists ─────────────────────────────────────────────────────────────────────
export const fetchSections = () =>
  req('/lists/sections').then((d) => d.sections ?? []);

export const fetchStudents = () =>
  req('/lists/students').then((d) => d.students ?? []);

// ── Materials ─────────────────────────────────────────────────────────────────
export function uploadMaterial(sectionId, title, file, description) {
  const form = new FormData();
  form.append('section_id', String(sectionId));
  form.append('title', title);
  form.append('file', file);
  form.append('material_type', 'pdf');
  if (description) form.append('description', description);
  return req('/materials/upload', { method: 'POST', body: form });
}

export const fetchMaterialsForSection = (sectionId) =>
  req(`/materials/section/${sectionId}`).then((d) => d.materials ?? []);

// ── Assignments ───────────────────────────────────────────────────────────────
export function createAssignment(body) {
  return req('/assignments/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

export function extractQuestionsFromPdf(file) {
  const form = new FormData();
  form.append('file', file);
  return req('/assignments/extract-questions-pdf', { method: 'POST', body: form });
}

export const fetchAssignmentsForSection = (sectionId) =>
  req(`/assignments/section/${sectionId}`).then((d) => d.assignments ?? []);

export const fetchAssignmentsForStudent = (studentId) =>
  req(`/assignments/student/${studentId}`).then((d) => d.assignments ?? []);

export const fetchAssignment = (assignmentId) =>
  req(`/assignments/${assignmentId}`);

// ── Submissions ───────────────────────────────────────────────────────────────
export const fetchSubmissionsForAssignment = (assignmentId) =>
  req(`/submissions/assignment/${assignmentId}`).then((d) => ({
    assignment_title: d.assignment_title ?? '',
    submissions: d.submissions ?? [],
  }));

export const fetchMySubmissions = (studentId) =>
  req(`/submissions/my/${studentId}`).then((d) => d.submissions ?? []);

export const fetchSubmission = (submissionId) =>
  req(`/submissions/${submissionId}`);

export function uploadSubmission(assignmentId, studentId, file, preFeedback) {
  const form = new FormData();
  form.append('assignment_id', String(assignmentId));
  form.append('student_id', String(studentId));
  form.append('file', file);
  if (preFeedback) form.append('pre_submission_feedback', preFeedback);
  return req('/submissions/upload', { method: 'POST', body: form });
}

// ── Grading ───────────────────────────────────────────────────────────────────
export function testSolution(assignmentId, studentId, file) {
  const form = new FormData();
  form.append('assignment_id', String(assignmentId));
  form.append('student_id', String(studentId));
  form.append('file', file);
  return req('/grading/test', { method: 'POST', body: form });
}

export function releaseGrade(submissionId, score, professorFeedback) {
  return req('/grading/release', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      submission_id: submissionId,
      score,
      professor_feedback: professorFeedback,
    }),
  });
}
