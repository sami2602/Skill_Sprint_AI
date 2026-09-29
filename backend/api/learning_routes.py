"""
SkillSprint AI — Learning Catalog & Quiz Execution API Endpoints
Handles course catalog listing, quiz loading, question evaluation, score calculation,
and persistent quiz attempt tracking in the SQLite database.
"""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.app.database import get_db
from backend.models.models import (
    Course, CourseModule, Quiz, QuizQuestion, QuizAttempt, User, Employee
)
from security.auth import get_current_active_user
from security.audit_service import AuditService

router = APIRouter(prefix="/api/v1/learning", tags=["Learning & Quiz System"])


@router.get("/courses", response_model=List[Dict[str, Any]])
def list_courses(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lists learning catalog courses and modules from database."""
    query = db.query(Course)
    if category:
        query = query.filter(Course.category.ilike(f"%{category}%"))
    courses = query.all()

    result = []
    for c in courses:
        modules = db.query(CourseModule).filter(CourseModule.course_id == c.course_id).order_by(CourseModule.sequence_order).all()
        result.append({
            "id": c.id,
            "course_id": c.course_id,
            "course_code": c.course_code,
            "title": c.title,
            "category": c.category,
            "difficulty": c.difficulty,
            "duration_hours": c.duration_hours,
            "description": c.description,
            "passing_score": c.passing_score,
            "modules": [
                {
                    "module_id": m.module_id,
                    "title": m.title,
                    "description": m.description,
                    "sequence_order": m.sequence_order
                } for m in modules
            ]
        })
    return result


@router.get("/quizzes", response_model=List[Dict[str, Any]])
def list_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lists available interactive quizzes."""
    quizzes = db.query(Quiz).all()
    result = []
    for q in quizzes:
        q_count = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == q.quiz_id).count()
        result.append({
            "id": q.id,
            "quiz_id": q.quiz_id,
            "title": q.title,
            "course_id": q.course_id,
            "module_id": q.module_id,
            "requirement_id": q.requirement_id,
            "passing_score": q.passing_score,
            "question_count": q_count
        })
    return result


@router.get("/quizzes/{quiz_id}", response_model=Dict[str, Any])
def get_quiz_detail(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieves quiz details and questions for interactive test execution."""
    qz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
    if not qz and quiz_id.isdigit():
        qz = db.query(Quiz).filter(Quiz.id == int(quiz_id)).first()

    if not qz:
        # Fallback to first quiz if not specified
        qz = db.query(Quiz).first()

    if not qz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz '{quiz_id}' not found.")

    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == qz.quiz_id).all()
    
    return {
        "quiz_id": qz.quiz_id,
        "title": qz.title,
        "course_id": qz.course_id,
        "module_id": qz.module_id,
        "requirement_id": qz.requirement_id,
        "passing_score": qz.passing_score,
        "questions": [
            {
                "question_id": q.question_id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": q.options_json,
                "explanation": q.explanation,
                "source_document_id": q.source_document_id,
                "source_section_id": q.source_section_id,
                "page_number": q.page_number
            } for q in questions
        ]
    }


@router.post("/quizzes/{quiz_id}/submit", response_model=Dict[str, Any])
def submit_quiz_attempt(
    quiz_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submits quiz answers, calculates exact score from database ground-truth answers,
    determines pass/fail status, and persists QuizAttempt record in SQLite database.
    """
    qz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
    if not qz and quiz_id.isdigit():
        qz = db.query(Quiz).filter(Quiz.id == int(quiz_id)).first()
    if not qz:
        qz = db.query(Quiz).first()
    if not qz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quiz '{quiz_id}' not found.")

    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == qz.quiz_id).all()
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz has no questions defined.")

    selected_index = payload.get("selected_option_index")
    question_id = payload.get("question_id")
    answers_map = payload.get("answers", {})

    correct_count = 0
    total_answered = 0
    detailed_results = []
    target_res = None

    for qst in questions:
        if question_id and qst.question_id == question_id:
            user_choice = selected_index
        else:
            user_choice = answers_map.get(qst.question_id, None)

        if user_choice is not None:
            total_answered += 1
            is_correct = (user_choice == qst.correct_option_index)
            if is_correct:
                correct_count += 1
        else:
            is_correct = False

        res = {
            "question_id": qst.question_id,
            "user_selected_index": user_choice,
            "correct_option_index": qst.correct_option_index,
            "is_correct": is_correct,
            "explanation": qst.explanation,
            "source_document_id": qst.source_document_id,
            "source_section_id": qst.source_section_id,
            "page_number": qst.page_number
        }
        detailed_results.append(res)
        if question_id and qst.question_id == question_id:
            target_res = res

    if question_id and target_res:
        passed = target_res["is_correct"]
        score_pct = 100.0 if passed else 0.0
    else:
        score_pct = (correct_count / total_answered * 100.0) if total_answered > 0 else 0.0
        passed = score_pct >= qz.passing_score

    # Persist Attempt in Database
    attempt_id = f"ATT-{uuid.uuid4().hex[:8].upper()}"
    attempt = QuizAttempt(
        attempt_id=attempt_id,
        user_id=current_user.user_id,
        employee_id=current_user.employee_id,
        quiz_id=qz.quiz_id,
        score=score_pct,
        passed=passed,
        answers_json=payload
    )
    db.add(attempt)
    db.commit()

    AuditService(db).log_event(
        event_type="QUIZ_ATTEMPTED",
        user_id=current_user.user_id,
        entity_type="QUIZ",
        entity_id=qz.quiz_id,
        new_value={"score": score_pct, "passed": passed, "attempt_id": attempt_id}
    )

    display_res = target_res or (detailed_results[0] if detailed_results else {})
    return {
        "attempt_id": attempt_id,
        "quiz_id": qz.quiz_id,
        "score": score_pct,
        "passed": passed,
        "passing_score": qz.passing_score,
        "results": detailed_results,
        "explanation": display_res.get("explanation", "Quiz attempt recorded."),
        "source_document_id": display_res.get("source_document_id", "DOC-SOP01"),
        "source_section_id": display_res.get("source_section_id", "ESC-4.2"),
        "page_number": display_res.get("page_number", 8)
    }

