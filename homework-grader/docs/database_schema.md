# Database Schema Documentation
## AI Homework Grading System - SF State CS Department

**Version:** 2.0 (Section-Centric Design)  
**Last Updated:** February 12, 2026

---

## Overview

This database schema is designed around **sections** as the core entity. A section represents a specific offering of a course (e.g., CSC 895-01 Spring 2026, taught by Prof. Smith on MW 2:00-3:30 PM).

### Key Design Principles

1. **Section-Centric**: Everything revolves around sections, not courses
2. **Independent Knowledge Cores**: Each section has its own vector store collection
3. **Custom Rubrics**: Professors can create section-specific grading rubrics
4. **Scalable**: Clean relationships that won't create maintenance nightmares
5. **Realistic**: Models real academic scenarios (multiple sections, same professor teaching multiple sections, etc.)

---

## Entity Relationship Diagram

```
Faculty (Professor)
   ↓ teaches (1:N)
Section ← Course (catalog entry)
   ↓ has (1:N)
   ├── Enrollment ← Student
   ├── Material (with vector store)
   ├── Rubric (grading criteria)
   └── Assignment
          ↓ receives (1:N)
       Submission ← Student
          ↓ has (1:1)
       Grade
          ↓ has (1:N)
       Feedback
```

---

## Tables

### 1. **faculty** (Professors/Instructors)

Represents professors and instructors in the CS department.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| first_name | String(100) | First name |
| last_name | String(100) | Last name |
| email | String(255) | Email (unique) |
| sfsu_id | String(50) | SF State faculty ID (unique) |
| department | String(100) | Department (default: "Computer Science") |
| is_active | Boolean | Account status |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `sections`: One faculty can teach many sections

**Example:**
```python
Faculty(
    first_name="Jane",
    last_name="Smith",
    email="jsmith@sfsu.edu",
    sfsu_id="FAC001"
)
```

---

### 2. **courses** (Course Catalog)

Represents course catalog entries (not specific offerings).

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| course_code | String(20) | Course code (unique, e.g., "CSC 895") |
| course_name | String(255) | Course name |
| description | Text | Course description |
| department | String(100) | Department |
| prerequisites | Text | Prerequisites |
| is_active | Boolean | Course status |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `sections`: One course can have many sections

**Example:**
```python
Course(
    course_code="CSC 895",
    course_name="Advanced Topics in AI",
    prerequisites="CSC 600 or equivalent"
)
```

---

### 3. **sections** ⭐ (Core Entity)

Represents a specific offering of a course.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| course_id | Integer | Foreign key to courses |
| faculty_id | Integer | Foreign key to faculty |
| section_number | String(10) | Section number (e.g., "01", "A") |
| semester | String(20) | Semester (e.g., "Spring", "Fall") |
| year | Integer | Year |
| days_of_week | String(20) | Class days (e.g., "MW", "TTh") |
| start_time | Time | Class start time |
| end_time | Time | Class end time |
| location | String(100) | Room/location |
| max_students | Integer | Maximum enrollment |
| vector_store_collection_id | String(255) | Unique ChromaDB collection ID |
| is_active | Boolean | Section status |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `course`: Belongs to one course
- `faculty`: Taught by one faculty member
- `enrollments`: Has many student enrollments
- `materials`: Has many course materials
- `assignments`: Has many assignments
- `rubrics`: Has many grading rubrics

**Properties:**
- `section_code`: Full code (e.g., "CSC 895-01")
- `enrolled_count`: Number of enrolled students
- `is_full`: Whether at capacity
- `schedule_display`: Human-readable schedule

**Example:**
```python
Section(
    course_id=1,
    faculty_id=1,
    section_number="01",
    semester="Spring",
    year=2026,
    days_of_week="MW",
    start_time=time(14, 0),
    end_time=time(15, 30),
    location="Thornton Hall 101",
    max_students=30,
    vector_store_collection_id="csc895_01_spring2026"
)
```

**Key Design Decision:**
- Each section has its own `vector_store_collection_id` for independent knowledge cores
- This allows CSC 895-01 and CSC 895-02 to have completely separate RAG knowledge bases

---

### 4. **students**

Represents students.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| first_name | String(100) | First name |
| last_name | String(100) | Last name |
| email | String(255) | Email (unique) |
| sfsu_id | String(50) | SF State student ID (unique) |
| is_active | Boolean | Account status |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `enrollments`: Enrolled in many sections
- `submissions`: Has many homework submissions

---

### 5. **enrollments**

Links students to specific sections.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| student_id | Integer | Foreign key to students |
| section_id | Integer | Foreign key to sections |
| enrollment_date | DateTime | When enrolled |
| status | String(20) | Status (active, dropped, completed) |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `student`: Belongs to one student
- `section`: Belongs to one section

**Example:**
```python
Enrollment(
    student_id=1,
    section_id=5,
    status="active"
)
```

---

### 6. **rubrics** (Grading Criteria)

Professor-defined grading criteria for sections.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| section_id | Integer | Foreign key to sections |
| rubric_name | String(255) | Rubric name |
| description | Text | Description |
| criteria | JSON | Structured grading categories |
| grading_instructions | Text | Natural language AI instructions |
| max_score | Float | Maximum score |
| is_active | Boolean | Rubric status |
| is_default | Boolean | Default for section |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `section`: Belongs to one section
- `assignments`: Can be used by many assignments

**Criteria JSON Structure:**
```json
{
  "categories": [
    {
      "name": "Correctness",
      "weight": 40,
      "description": "Does the code work?",
      "criteria": ["All tests pass", "Edge cases handled"]
    },
    {
      "name": "Code Quality",
      "weight": 30,
      "description": "Is code well-written?",
      "criteria": ["Readable", "Documented", "DRY"]
    }
  ]
}
```

**Validation:**
- Category weights must sum to 100
- At least one category required
- Each category needs name, weight, description

---

### 7. **materials** (Course Materials)

Course materials specific to sections.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| section_id | Integer | Foreign key to sections |
| title | String(255) | Material title |
| description | Text | Description |
| material_type | Enum | Type (pdf, textbook, notes, slides, etc.) |
| file_name | String(255) | Original filename |
| file_path | String(500) | Storage path |
| file_size | Integer | Size in bytes |
| mime_type | String(100) | MIME type |
| vector_store_document_ids | Text | JSON array of document IDs in vector store |
| is_indexed | Integer | Indexing status (0=no, 1=yes) |
| chunk_count | Integer | Number of chunks created |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `section`: Belongs to one section

**Key Design:**
- Materials are stored in the section's vector store collection
- `vector_store_document_ids` tracks which documents in ChromaDB came from this material
- Each section has isolated materials for RAG

---

### 8. **assignments**

Homework/assignments for sections.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| section_id | Integer | Foreign key to sections |
| rubric_id | Integer | Foreign key to rubrics (optional) |
| title | String(255) | Assignment title |
| description | Text | Description |
| grading_instructions | Text | Natural language instructions (fallback) |
| max_score | Float | Maximum score |
| due_date | DateTime | Due date |
| late_submission_allowed | Boolean | Allow late submissions |
| late_penalty_percent | Float | Penalty per day |
| attachment_file_name | String(255) | Attachment filename (optional) |
| attachment_file_path | String(500) | Attachment path (optional) |
| is_published | Boolean | Published status |
| is_active | Boolean | Active status |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `section`: Belongs to one section
- `rubric`: Can use one rubric (optional)
- `submissions`: Has many student submissions

**Grading Strategy:**
1. If `rubric_id` is set, use that rubric for grading
2. Otherwise, use `grading_instructions` (natural language)
3. Can use both for additional context

---

### 9. **submissions**

Student homework submissions.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| assignment_id | Integer | Foreign key to assignments |
| student_id | Integer | Foreign key to students |
| submission_text | Text | Text-based submission |
| file_name | String(255) | Filename (if file upload) |
| file_path | String(500) | File storage path |
| file_size | Integer | File size in bytes |
| submission_date | DateTime | Submission timestamp |
| attempt_number | Integer | Attempt number |
| status | Enum | Status (submitted, grading, graded, returned) |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `assignment`: Belongs to one assignment
- `student`: Belongs to one student
- `grade`: Has one grade (1:1)

---

### 10. **grades**

Grading results for submissions.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| submission_id | Integer | Foreign key to submissions (unique) |
| score | Float | Actual score |
| max_score | Float | Maximum possible |
| percentage | Float | Percentage score |
| grading_criteria | JSON | Structured grading breakdown |
| ai_confidence | Float | AI confidence (0-1) |
| summary | Text | Overall summary |
| strengths | Text | What was done well |
| weaknesses | Text | What needs improvement |
| suggestions | Text | Improvement suggestions |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `submission`: Belongs to one submission
- `feedback_items`: Has many detailed feedback items

**Properties:**
- `letter_grade`: Computed letter grade (A, B+, C, etc.)

---

### 11. **feedback**

Detailed category-specific feedback.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| grade_id | Integer | Foreign key to grades |
| category | Enum | Category (correctness, code_quality, etc.) |
| title | String(255) | Feedback title |
| comment | Text | Detailed comment |
| category_score | Integer | Score for this category |
| category_max_score | Integer | Max score for category |
| line_start | Integer | Line number (for code) |
| line_end | Integer | End line number |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `grade`: Belongs to one grade

---

## Realistic Scenarios Supported

### Scenario 1: Multiple Sections of Same Course
```
CSC 895 "Advanced AI"
├── Section 01 (Prof. Smith, MW 2:00-3:30)
│   ├── Vector Store: csc895_01_spring2026
│   ├── Materials: Prof. Smith's slides
│   └── Students: Alice, Bob, Carol
└── Section 02 (Prof. Chen, TTh 4:00-5:30)
    ├── Vector Store: csc895_02_spring2026
    ├── Materials: Prof. Chen's slides (different!)
    └── Students: David, Emma
```

**Result:** Each section has independent knowledge base for grading.

### Scenario 2: Same Professor, Multiple Sections
```
Prof. Smith
├── CSC 895-01 (Spring 2026, MW)
├── CSC 600-01 (Spring 2026, MWF)
└── CSC 600-02 (Spring 2026, TTh)
```

**Result:** Professor can manage multiple sections with different materials/rubrics.

### Scenario 3: Student Enrolled in Multiple Sections
```
Student: Alice
├── CSC 895-01 (Section 1)
├── CSC 667-02 (Section 4)
└── CSC 600-01 (Section 6)
```

**Result:** Student submissions are tracked per section.

### Scenario 4: Section-Specific Rubrics
```
CSC 667-01 (Prof. Chen)
└── Rubric: "Software Engineering Rubric"
    ├── Requirements: 35%
    ├── Design: 25%
    ├── Testing: 20%
    └── Code Quality: 20%

CSC 667-02 (Prof. Johnson)
└── Rubric: "Agile Development Rubric" (different!)
    ├── User Stories: 30%
    ├── Sprint Execution: 30%
    ├── Team Collaboration: 20%
    └── Code Review: 20%
```

**Result:** Same course, different sections, different grading approaches.

---

## Vector Store Architecture

### Collection Naming Convention
```
{course_code}_{section_number}_{semester}{year}
```

Examples:
- `csc895_01_spring2026`
- `csc667_02_fall2025`
- `csc600_03_summer2026`

### Benefits
1. **Isolation**: Each section's materials are completely separate
2. **Accuracy**: Grading uses only relevant materials for that section
3. **Scalability**: Easy to archive old sections
4. **Performance**: Smaller, focused collections = faster queries

---

## Edge Cases Handled

### 1. Section at Capacity
```python
if section.is_full:
    return "Section is full"
```

### 2. Student Drops Section
```python
enrollment.status = "dropped"
```

### 3. Faculty Leaves Department
```python
faculty.is_active = False
# Sections remain, can be reassigned
```

### 4. Course Discontinued
```python
course.is_active = False
# Historical sections preserved
```

### 5. Rubric Validation
```python
rubric.validate_criteria()
# Ensures weights sum to 100
```

### 6. Late Submissions
```python
if assignment.is_overdue() and not assignment.late_submission_allowed:
    return "Late submissions not allowed"
```

---

## Indexes for Performance

Key indexes for fast queries:

1. `sections.course_id` - Find all sections of a course
2. `sections.faculty_id` - Find all sections taught by professor
3. `enrollments.student_id` - Find student's enrollments
4. `enrollments.section_id` - Find section's students
5. `materials.section_id` - Find section's materials
6. `assignments.section_id` - Find section's assignments

---

## Migration Path

To migrate from old schema to new:

1. Create `sections` table
2. Create `rubrics` table
3. Migrate data:
   - Create one section per old course
   - Link materials/assignments to sections
   - Update enrollments to reference sections
4. Drop old constraints
5. Add new constraints

---

## Summary

This schema is:
- ✅ **Section-centric** - Everything organized by sections
- ✅ **Scalable** - Clean relationships, easy to maintain
- ✅ **Realistic** - Models real academic scenarios
- ✅ **Isolated** - Independent knowledge cores per section
- ✅ **Flexible** - Supports custom rubrics and grading
- ✅ **Performant** - Proper indexes and normalized structure

**Total Tables:** 11  
**Core Entity:** Section  
**Key Innovation:** Section-specific vector store collections

---

**Last Updated:** February 12, 2026
