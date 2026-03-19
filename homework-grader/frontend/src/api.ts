/**
 * API client for backend. All requests use relative URLs so dev server proxy applies.
 */

// When running standalone (port 3001) the webpack dev server proxies /grading
// to the backend. When embedded in the AI-Tutor frontend the same proxy applies.
const BASE = '/grading';

// ============== Shared types ==============

export interface SectionOption {
  id: number;
  section_number: string;
  semester: string;
  year: number;
  section_code: string;
  course_code: string | null;
  course_name: string | null;
}

export interface StudentOption {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  sfsu_id: string;
}

// ============== Lists ==============

export async function fetchSections(): Promise<SectionOption[]> {
  const res = await fetch(`${BASE}/api/v1/lists/sections`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.sections ?? [];
}

export async function fetchStudents(): Promise<StudentOption[]> {
  const res = await fetch(`${BASE}/api/v1/lists/students`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.students ?? [];
}

// ============== Materials ==============

export async function uploadMaterial(
  sectionId: number,
  title: string,
  file: File,
  description?: string
): Promise<{ success: boolean }> {
  const form = new FormData();
  form.append('section_id', String(sectionId));
  form.append('title', title);
  form.append('file', file);
  form.append('material_type', 'pdf');
  if (description) form.append('description', description);
  const res = await fetch(`${BASE}/api/v1/materials/upload`, { method: 'POST', body: form });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

export async function fetchMaterialsForSection(sectionId: number): Promise<{ materials: Array<{ id: number; title: string; file_name: string }> }> {
  const res = await fetch(`${BASE}/api/v1/materials/section/${sectionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ============== Assignments (PV) ==============

export interface AssignmentDetail {
  id: number;
  title: string;
  description: string | null;
  questions_content: string | null;
  section_id: number;
  section_code: string | null;
  release_at: string | null;
  due_date: string | null;
  max_score: number;
  grading_instructions: string | null;
  late_submission_allowed: boolean;
}

export interface AssignmentForPV {
  id: number;
  title: string;
  description: string | null;
  questions_content: string | null;
  release_at: string | null;
  due_date: string | null;
  max_score: number;
  submission_count: number;
}

export interface AssignmentForSV {
  id: number;
  title: string;
  description: string | null;
  questions_content: string | null;
  section_id: number;
  section_code: string | null;
  release_at: string | null;
  due_date: string | null;
  max_score: number;
  late_submission_allowed: boolean;
}

export async function createAssignment(body: {
  section_id: number;
  title: string;
  description?: string;
  questions_content?: string;
  grading_instructions?: string;
  max_score?: number;
}): Promise<{ success: boolean; assignment: { id: number } }> {
  const res = await fetch(`${BASE}/api/v1/assignments/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

export async function extractQuestionsFromPdf(file: File): Promise<{ text: string; num_pages: number }> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/api/v1/assignments/extract-questions-pdf`, { method: 'POST', body: form });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

export async function fetchAssignmentsForSection(sectionId: number): Promise<{ assignments: AssignmentForPV[] }> {
  const res = await fetch(`${BASE}/api/v1/assignments/section/${sectionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchAssignmentsForStudent(studentId: number): Promise<{ assignments: AssignmentForSV[] }> {
  const res = await fetch(`${BASE}/api/v1/assignments/student/${studentId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchAssignment(assignmentId: number): Promise<AssignmentDetail> {
  const res = await fetch(`${BASE}/api/v1/assignments/${assignmentId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ============== Submissions ==============

export interface SubmissionForAssignment {
  id: number;
  student_id: number;
  student_name: string | null;
  file_name: string | null;
  submission_date: string;
  attempt_number: number;
  status: string;
  pre_submission_feedback: string | null;
  has_grade_released: boolean;
}

export interface MySubmission {
  id: number;
  assignment_id: number;
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
}

export interface SubmissionDetail {
  id: number;
  assignment_id: number;
  assignment_title: string | null;
  student_id: number;
  student_name: string | null;
  file_name: string | null;
  file_path: string | null;
  submission_date: string;
  status: string;
  pre_submission_feedback: string | null;
  grade: { score: number; max_score: number; professor_feedback: string | null; is_released: boolean } | null;
}

export async function fetchSubmissionsForAssignment(assignmentId: number): Promise<{
  assignment_title: string;
  submissions: SubmissionForAssignment[];
}> {
  const res = await fetch(`${BASE}/api/v1/submissions/assignment/${assignmentId}`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return { assignment_title: data.assignment_title ?? '', submissions: data.submissions ?? [] };
}

export async function fetchMySubmissions(studentId: number): Promise<{ submissions: MySubmission[] }> {
  const res = await fetch(`${BASE}/api/v1/submissions/my/${studentId}`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return { submissions: data.submissions ?? [] };
}

export async function fetchSubmission(submissionId: number): Promise<SubmissionDetail> {
  const res = await fetch(`${BASE}/api/v1/submissions/${submissionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadSubmission(
  assignmentId: number,
  studentId: number,
  file: File,
  preSubmissionFeedback?: string
): Promise<{ success: boolean; submission?: { id: number } }> {
  const form = new FormData();
  form.append('assignment_id', String(assignmentId));
  form.append('student_id', String(studentId));
  form.append('file', file);
  if (preSubmissionFeedback) form.append('pre_submission_feedback', preSubmissionFeedback);
  const res = await fetch(`${BASE}/api/v1/submissions/upload`, { method: 'POST', body: form });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

// ============== Grading ==============

export interface TestFeedbackResult {
  success: boolean;
  feedback: {
    score: number;
    max_score: number;
    percentage: number;
    summary: string;
    strengths: string;
    weaknesses: string;
    suggestions: string;
  };
}

export async function testSolution(
  assignmentId: number,
  studentId: number,
  file: File
): Promise<TestFeedbackResult> {
  const form = new FormData();
  form.append('assignment_id', String(assignmentId));
  form.append('student_id', String(studentId));
  form.append('file', file);
  const res = await fetch(`${BASE}/api/v1/grading/test`, { method: 'POST', body: form });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

export async function releaseGrade(
  submissionId: number,
  score: number,
  professorFeedback: string
): Promise<{ success: boolean }> {
  const res = await fetch(`${BASE}/api/v1/grading/release`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ submission_id: submissionId, score, professor_feedback: professorFeedback }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}
