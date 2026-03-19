# Professor View (PV) & Student View (SV) Implementation

This document describes the changes made to implement the full professor–student workflow with test-before-submit, release dates, optional AI grading instructions, and professor-grade release.

---

## Overview

The system now has two distinct views:

- **Professor View (PV)**: Select course/section, upload materials, create assignments (with release date + optional AI grading instructions), and grade submissions with manual feedback.
- **Student View (SV)**: View released assignments, homework questions, upload solution, **Test** (AI feedback without submitting), **Submit** (submit for professor review). After submit, view last test feedback + disclaimer. When professor releases grade, view professor feedback + score.

---

## 1. Database Changes

### New / Modified Tables

| Table | Changes |
|-------|---------|
| **assignments** | `release_at` (DateTime, required) – when assignment becomes visible to students; `questions_content` (Text, optional) – homework questions (Markdown/HTML) |
| **submissions** | `pre_submission_feedback` (Text/JSON, optional) – last AI test feedback before submit, shown to professor when grading |
| **grades** | `professor_feedback` (Text, optional); `is_released` (Boolean, default False) |
| **test_feedback** | **New table** – stores latest AI test feedback per (assignment_id, student_id); overwritten on each test; copied to submission.pre_submission_feedback when student submits |

### Model Files

- `backend/app/models/assignment.py` – added `questions_content`, `release_at`
- `backend/app/models/submission.py` – added `pre_submission_feedback`
- `backend/app/models/grade.py` – added `professor_feedback`, `is_released`
- `backend/app/models/test_feedback.py` – new model

---

## 2. API Endpoints

### Assignments (`/api/v1/assignments`)

- `POST /extract-questions-pdf` – Extract text from homework questions PDF (returns `text`, `num_pages`); used by PV to populate questions_content.
- `POST /` – Create assignment (section_id, title, description, questions_content, grading_instructions optional, max_score). release_at and due_date are set automatically (now, now+14 days). Assignments are visible to enrolled students immediately.
- `GET /section/{section_id}` – List assignments for section (PV)
- `GET /student/{student_id}` – List assignments for student (SV: enrolled sections only)
- `GET /{assignment_id}` – Get assignment detail

### Submissions (`/api/v1/submissions`)

- `POST /upload` – Upload submission (file, assignment_id, student_id; optional pre_submission_feedback). If not provided, backend copies from TestFeedback.
- `GET /assignment/{assignment_id}` – List submissions (includes pre_submission_feedback, has_grade_released)
- `GET /my/{student_id}` – List submissions for a student (SV)
- `GET /{submission_id}` – Get submission (includes pre_submission_feedback, grade if present)

### Grading (`/api/v1/grading`)

- `POST /test` – **Test-only**: file + assignment_id + student_id. Runs AI grading, stores result in TestFeedback (overwrites), returns feedback. Does NOT create submission.
- `POST /grade` – (existing) Auto-grade submission with AI – optional for PV.
- `POST /release` – Professor releases grade: submission_id, score, professor_feedback. Creates/updates Grade, sets is_released=True, submission.status=RETURNED.
- `GET /grade/{submission_id}` – Get grade (includes professor_feedback, is_released)

---

## 3. Backend Logic

### Grading Instructions

- No hardcoded fallback. If `assignment.grading_instructions` is null/empty, use:  
  *"Grade based on the provided course materials and homework context. Provide constructive feedback on correctness, completeness, and clarity."*
- AI can grade solely from materials + homework questions + student solution when instructions are omitted.

### Test Flow

1. Student uploads PDF, clicks **Test**.
2. Backend runs grading, overwrites `test_feedback` for (assignment_id, student_id), returns feedback.
3. Student can iterate (test again).
4. Student clicks **Submit** → backend creates Submission, copies TestFeedback into submission.pre_submission_feedback, deletes TestFeedback row.

### Professor Release Flow

1. Professor sees submissions, clicks one.
2. Professor sees AI feedback (from pre_submission_feedback) and solution info.
3. Professor enters score + professor_feedback.
4. Professor clicks **Release** → Grade created/updated with professor_feedback, is_released=True; submission.status=RETURNED.
5. Student sees professor feedback + score in My Submissions.

---

## 4. Frontend Structure

### Layout

- **View switcher**: Professor View | Student View
- **PV tabs**: Upload Materials | Create Assignment | Grade Submissions
- **SV tabs**: My Assignments | My Submissions
- **SV student picker**: Dropdown to select student (demo)

### Professor View Pages

- **PVMaterials**: Section dropdown, title, description, file upload; list materials for section
- **PVCreateAssignment**: Section, title, description, **homework questions** (paste text or upload PDF; PDF text is extracted and populated in the textarea; you can edit after upload), grading_instructions (optional), max_score. Assignments are visible to enrolled students immediately.
- **PVGradeSubmissions**: Section → Assignment → Submissions list; click submission → view AI feedback, enter score + professor feedback, Release

### Student View Pages

- **SVAssignments**: List released assignments for selected student
- **SVAssignmentDetail**: View questions (Canvas-like), upload PDF, **Test with AI**, **Submit for professor**; after submit, show last test feedback + disclaimer
- **SVMySubmissions**: List submissions with pre_submission_feedback and released grades

### UI

- Clean, modern layout
- Card-based components
- Clear labels, status messages, disclaimers

---

## 5. File Changes Summary

### Backend

- `app/models/assignment.py` – release_at, questions_content
- `app/models/submission.py` – pre_submission_feedback
- `app/models/grade.py` – professor_feedback, is_released
- `app/models/test_feedback.py` – new
- `app/models/__init__.py` – export TestFeedback
- `app/services/grading/__init__.py` – grade_test_only, optional grading instructions
- `app/api/v1/assignments.py` – new router, `POST /extract-questions-pdf` for PDF upload
- `app/api/v1/submissions.py` – pre_submission_feedback, TestFeedback copy, my submissions
- `app/api/v1/grading.py` – test, release endpoints
- `app/main.py` – include assignments router
- `scripts/seed_realistic_data.py` – minimal seed: CSC 810 only, students 1–3 enrolled

### Frontend

- `src/App.tsx` – PV/SV switcher, nav, routing
- `src/pages/pv/PVMaterials.tsx` – upload materials
- `src/pages/pv/PVCreateAssignment.tsx` – create assignment
- `src/pages/pv/PVGradeSubmissions.tsx` – grade submissions, release
- `src/pages/sv/SVAssignments.tsx` – my assignments list
- `src/pages/sv/SVAssignmentDetail.tsx` – questions, Test, Submit
- `src/pages/sv/SVMySubmissions.tsx` – my submissions
- `src/api.ts` – all new API functions
- `src/index.css` – layout, form, card styles

---

## 6. Run & Test

1. **Reset DB**:  
   ```bash
   cd backend && ../venv/bin/python -c "
   from app.db.session import engine, Base
   from app.models import Faculty, Course, Section, Student, Enrollment, Rubric, Assignment, Material, Submission, Grade, Feedback, TestFeedback
   Base.metadata.drop_all(bind=engine)
   Base.metadata.create_all(bind=engine)
   "
   ```

2. **Seed**:  
   ```bash
   ./venv/bin/python scripts/seed_realistic_data.py
   ```

3. **Backend**: `cd backend && uvicorn app.main:app --reload`

4. **Frontend**: `cd frontend && npm start`

5. **PV flow**: Select section → Upload material → Create assignment (set release_at to now or past) → Grade Submissions → select submission → enter score + feedback → Release

6. **SV flow**: Select student → My Assignments → click assignment → view questions → upload PDF → Test → Submit → see last test feedback + disclaimer → My Submissions for released grades
