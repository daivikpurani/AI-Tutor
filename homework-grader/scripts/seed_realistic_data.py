#!/usr/bin/env python3
"""
Seed database with minimal data for workflow testing.

- 1 course: CSC 810
- 1 section: CSC 810-01
- 3 students: Alice, Bob, Carol (ids 1, 2, 3)
- Students 1-3 enrolled only in CSC 810-01
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, time

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.core.logging import setup_logging, logger

# Import all models
from app.models import (
    Faculty,
    Course,
    Section,
    Student,
    Enrollment,
    Rubric,
    Assignment,
)


def seed_realistic_data():
    """Seed database with minimal CS Department data for testing."""
    db = SessionLocal()

    try:
        logger.info("=" * 80)
        logger.info("DATABASE SEEDING - MINIMAL (CSC 810 only)")
        logger.info("=" * 80)

        # =====================================================================
        # CREATE FACULTY
        # =====================================================================
        logger.info("\n[1/6] Creating faculty...")
        faculty = Faculty(
            first_name="Kaz",
            last_name="Okada",
            email="kazokada@sfsu.edu",
            sfsu_id="FAC001",
            department="Computer Science",
            is_active=True,
        )
        db.add(faculty)
        db.flush()
        logger.info(f"  ✓ {faculty.full_name}")

        # =====================================================================
        # CREATE COURSE
        # =====================================================================
        logger.info("\n[2/6] Creating course...")
        course = Course(
            course_code="CSC 810",
            course_name="Analysis of Algorithms II",
            description="Advanced algorithms and their analysis.",
            department="Computer Science",
            prerequisites="CSC 410",
            is_active=True,
        )
        db.add(course)
        db.flush()
        logger.info(f"  ✓ {course.course_code}: {course.course_name}")

        # =====================================================================
        # CREATE SECTION
        # =====================================================================
        logger.info("\n[3/6] Creating section...")
        section = Section(
            course_id=course.id,
            faculty_id=faculty.id,
            section_number="01",
            semester="Spring",
            year=2026,
            days_of_week="TTh",
            start_time=time(17, 0),
            end_time=time(18, 30),
            location="Thornton Hall 804",
            max_students=30,
            vector_store_collection_id="csc810_01_spring2026",
            is_active=True,
        )
        db.add(section)
        db.flush()
        logger.info(f"  ✓ {course.course_code}-{section.section_number}")

        # =====================================================================
        # CREATE STUDENTS (3 only)
        # =====================================================================
        logger.info("\n[4/6] Creating students...")
        students = [
            Student(first_name="Alice", last_name="Anderson", email="aalice@mail.sfsu.edu", sfsu_id="STU001", is_active=True),
            Student(first_name="Bob", last_name="Brown", email="bbrown@mail.sfsu.edu", sfsu_id="STU002", is_active=True),
            Student(first_name="Carol", last_name="Chen", email="cchen@mail.sfsu.edu", sfsu_id="STU003", is_active=True),
        ]
        db.add_all(students)
        db.flush()
        for s in students:
            logger.info(f"  ✓ {s.full_name} (id={s.id})")

        # =====================================================================
        # CREATE ENROLLMENTS (only students 1, 2, 3 in CSC 810-01)
        # =====================================================================
        logger.info("\n[5/6] Creating enrollments...")
        for student in students:
            db.add(Enrollment(student_id=student.id, section_id=section.id, status="active"))
        db.flush()
        logger.info(f"  ✓ Students 1, 2, 3 enrolled in CSC 810-01")

        # =====================================================================
        # CREATE RUBRIC & ASSIGNMENT
        # =====================================================================
        logger.info("\n[6/6] Creating rubric and assignment...")
        rubric = Rubric(
            section_id=section.id,
            rubric_name="CSC 810 Assignment Rubric",
            description="Standard rubric for algorithms assignments",
            criteria={"categories": []},
            grading_instructions="Grade based on correctness and clarity.",
            max_score=100.0,
            is_active=True,
            is_default=True,
        )
        db.add(rubric)
        db.flush()

        now = datetime.utcnow()
        assignment = Assignment(
            section_id=section.id,
            rubric_id=rubric.id,
            title="Homework 1: Analysis of Algorithms",
            description="Analyze the efficiency of the given algorithm.",
            questions_content="## Instructions\nProvide Big-O analysis and correctness argument for the given algorithm.",
            grading_instructions="Evaluate correctness of analysis and clarity of exposition.",
            max_score=100.0,
            release_at=now,
            due_date=now + timedelta(days=14),
            late_submission_allowed=False,
            is_published=True,
            is_active=True,
        )
        db.add(assignment)
        db.flush()
        logger.info(f"  ✓ Rubric and 1 assignment created")

        # =====================================================================
        # COMMIT
        # =====================================================================
        db.commit()

        logger.info("\n" + "=" * 80)
        logger.info("SEEDING COMPLETE")
        logger.info("=" * 80)
        logger.info("\nSummary:")
        logger.info("  • Faculty: 1")
        logger.info("  • Course: CSC 810")
        logger.info("  • Section: CSC 810-01")
        logger.info("  • Students: 3 (Alice, Bob, Carol)")
        logger.info("  • Enrollments: 3 (all in CSC 810-01)")
        logger.info("  • Assignments: 1")
        logger.info("\nWorkflow: PV creates assignment for CSC 810-01 → SV (students 1–3) sees it.")
        logger.info("")

    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        db.rollback()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    setup_logging()
    seed_realistic_data()
