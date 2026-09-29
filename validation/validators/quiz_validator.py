"""
SkillSprint AI — Independent Quiz & Distractor Validator
Verifies quiz question structure, option consistency, correct answer validity, distractor uniqueness, and source policy backing without GenAI calls.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.models import PolicyRequirement, Document


class QuizValidator:
    """Independently verifies quiz structures, correct answers, and distractors (FR-31)."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def validate(self, plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validates all quizzes across modules in plan.
        Returns list of quiz_errors.
        """
        all_reqs = {r.requirement_id: r for r in self.db.query(PolicyRequirement).all()}
        all_docs = {d.doc_id: d for d in self.db.query(Document).filter(Document.is_active == True).all()}

        quiz_errors: List[Dict[str, Any]] = []

        modules = plan_data.get("modules", [])
        for mod in modules:
            mod_id = mod.get("module_id", "MOD-UNKNOWN")
            quizzes = mod.get("quizzes", [])

            for quiz in quizzes:
                quiz_id = quiz.get("quiz_id", "QZ-UNKNOWN")
                quiz_title = quiz.get("title", "Untitled Quiz")
                questions = quiz.get("questions", [])

                if not questions:
                    quiz_errors.append({
                        "quiz_id": quiz_id,
                        "question_id": "NONE",
                        "reason": f"Quiz '{quiz_title}' contains zero questions.",
                        "evidence": "Quizzes must contain at least one question."
                    })
                    continue

                for qst in questions:
                    qst_id = qst.get("question_id", "QST-UNKNOWN")
                    q_text = qst.get("question_text", "Untitled Question")
                    correct_answer_id = qst.get("correct_answer_id")
                    options = qst.get("options", [])
                    req_id = qst.get("requirement_id")
                    cit = qst.get("source_citation")

                    # 1. Option count check (minimum 2 options)
                    if not options or len(options) < 2:
                        quiz_errors.append({
                            "quiz_id": quiz_id,
                            "question_id": qst_id,
                            "reason": f"Quiz question '{qst_id}' has fewer than 2 answer choices.",
                            "evidence": f"Found {len(options) if options else 0} options; minimum 2 required."
                        })

                    # 2. Correct answer existence in options
                    option_ids = [opt.get("option_id") if isinstance(opt, dict) else getattr(opt, "option_id", "") for opt in options]
                    if not correct_answer_id or correct_answer_id not in option_ids:
                        quiz_errors.append({
                            "quiz_id": quiz_id,
                            "question_id": qst_id,
                            "reason": f"Correct answer ID '{correct_answer_id}' does not match any option ID ({option_ids}).",
                            "evidence": f"Declared correct answer '{correct_answer_id}' is missing from options."
                        })

                    # 3. Matching option is_correct flag consistency
                    correct_opts = [opt for opt in options if (opt.get("is_correct") if isinstance(opt, dict) else getattr(opt, "is_correct", False))]
                    if len(correct_opts) == 0:
                        quiz_errors.append({
                            "quiz_id": quiz_id,
                            "question_id": qst_id,
                            "reason": "No option is marked is_correct = True.",
                            "evidence": "Every multiple choice question must have exactly one correct option."
                        })
                    elif len(correct_opts) > 1 and qst.get("question_type", "MULTIPLE_CHOICE") == "MULTIPLE_CHOICE":
                        quiz_errors.append({
                            "quiz_id": quiz_id,
                            "question_id": qst_id,
                            "reason": f"Multiple options ({[opt.get('option_id') for opt in correct_opts]}) are marked is_correct = True.",
                            "evidence": "Single choice question has multiple options marked correct."
                        })
                    else:
                        # Verify the marked correct option matches correct_answer_id
                        marked_id = correct_opts[0].get("option_id") if isinstance(correct_opts[0], dict) else getattr(correct_opts[0], "option_id", None)
                        if marked_id != correct_answer_id:
                            quiz_errors.append({
                                "quiz_id": quiz_id,
                                "question_id": qst_id,
                                "reason": f"Mismatch between correct_answer_id '{correct_answer_id}' and is_correct=True option '{marked_id}'.",
                                "evidence": f"Question metadata specifies '{correct_answer_id}' but option '{marked_id}' has is_correct=True."
                            })

                    # 4. Distractor uniqueness check (no duplicate option texts)
                    option_texts = [str(opt.get("option_text", "")).strip().lower() for opt in options]
                    if len(set(option_texts)) < len(option_texts):
                        quiz_errors.append({
                            "quiz_id": quiz_id,
                            "question_id": qst_id,
                            "reason": "Duplicate distractor option text detected.",
                            "evidence": "Answer options contain duplicate text choices."
                        })

                    # 5. Empty distractor check
                    for opt in options:
                        o_text = str(opt.get("option_text", "")).strip()
                        if not o_text:
                            quiz_errors.append({
                                "quiz_id": quiz_id,
                                "question_id": qst_id,
                                "reason": f"Option choice '{opt.get('option_id')}' has empty text.",
                                "evidence": "Option text cannot be blank."
                            })

                    # 6. Requirement mapping check
                    if req_id and req_id not in all_reqs:
                        quiz_errors.append({
                            "quiz_id": quiz_id,
                            "question_id": qst_id,
                            "reason": f"Question maps to invalid policy requirement ID '{req_id}'.",
                            "evidence": f"Requirement '{req_id}' missing from matrix."
                        })

                    # 7. Source policy grounding check
                    if not cit:
                        quiz_errors.append({
                            "quiz_id": quiz_id,
                            "question_id": qst_id,
                            "reason": "Question is missing source policy citation.",
                            "evidence": "All quiz questions must cite their source policy document."
                        })
                    else:
                        c_doc_id = cit.get("doc_id") if isinstance(cit, dict) else getattr(cit, "doc_id", None)
                        if c_doc_id and c_doc_id not in all_docs:
                            quiz_errors.append({
                                "quiz_id": quiz_id,
                                "question_id": qst_id,
                                "reason": f"Question citation references inactive or missing document '{c_doc_id}'.",
                                "evidence": f"Document '{c_doc_id}' not active in database."
                            })

        return quiz_errors
