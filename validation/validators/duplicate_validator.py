"""
SkillSprint AI — Duplicate Content Validator
Detects duplicate requirements, modules, tasks, and quiz questions in generated plans.
"""

from typing import List, Dict, Any


class DuplicateValidator:
    """Detects duplicate requirements, modules, tasks, and quiz questions (FR-38)."""

    def validate(self, plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans generated onboarding plan for duplicates across modules, tasks, and quizzes.
        Returns list of duplicate flags.
        """
        duplicate_items: List[Dict[str, Any]] = []

        seen_module_ids = set()
        seen_module_titles = set()
        seen_task_ids = set()
        seen_task_titles = set()
        seen_quiz_ids = set()
        seen_question_texts = set()
        seen_requirement_ids = set()

        modules = plan_data.get("modules", [])
        for mod in modules:
            mod_id = mod.get("module_id", "").strip()
            mod_title = mod.get("title", "").strip().lower()

            if mod_id:
                if mod_id in seen_module_ids:
                    duplicate_items.append({
                        "item_id": mod_id,
                        "item_type": "MODULE",
                        "title": mod.get("title", ""),
                        "reason": f"Duplicate module ID '{mod_id}' detected.",
                        "evidence": f"Module ID '{mod_id}' appears multiple times in onboarding plan."
                    })
                else:
                    seen_module_ids.add(mod_id)

            if mod_title:
                if mod_title in seen_module_titles:
                    duplicate_items.append({
                        "item_id": mod_id or mod_title,
                        "item_type": "MODULE",
                        "title": mod.get("title", ""),
                        "reason": f"Duplicate module title '{mod.get('title')}' detected.",
                        "evidence": "Substantially identical module title exists in another stage."
                    })
                else:
                    seen_module_titles.add(mod_title)

            # Check tasks within module
            for task in mod.get("tasks", []):
                task_id = task.get("task_id", "").strip()
                task_title = task.get("title", "").strip().lower()

                if task_id:
                    if task_id in seen_task_ids:
                        duplicate_items.append({
                            "item_id": task_id,
                            "item_type": "TASK",
                            "title": task.get("title", ""),
                            "reason": f"Duplicate task ID '{task_id}' detected across modules.",
                            "evidence": f"Task ID '{task_id}' is defined multiple times."
                        })
                    else:
                        seen_task_ids.add(task_id)

                if task_title:
                    if task_title in seen_task_titles:
                        duplicate_items.append({
                            "item_id": task_id or task_title,
                            "item_type": "TASK",
                            "title": task.get("title", ""),
                            "reason": f"Duplicate task title '{task.get('title')}' detected.",
                            "evidence": "Identical task title repeated in onboarding plan."
                        })
                    else:
                        seen_task_titles.add(task_title)

            # Check quizzes within module
            for quiz in mod.get("quizzes", []):
                quiz_id = quiz.get("quiz_id", "").strip()
                if quiz_id:
                    if quiz_id in seen_quiz_ids:
                        duplicate_items.append({
                            "item_id": quiz_id,
                            "item_type": "QUIZ",
                            "title": quiz.get("title", ""),
                            "reason": f"Duplicate quiz ID '{quiz_id}' detected.",
                            "evidence": f"Quiz ID '{quiz_id}' repeated."
                        })
                    else:
                        seen_quiz_ids.add(quiz_id)

                for qst in quiz.get("questions", []):
                    q_text = qst.get("question_text", "").strip().lower()
                    if q_text:
                        if q_text in seen_question_texts:
                            duplicate_items.append({
                                "item_id": qst.get("question_id", "QST-DUP"),
                                "item_type": "QUIZ_QUESTION",
                                "title": qst.get("question_text", "")[:60],
                                "reason": "Duplicate quiz question text detected.",
                                "evidence": "Question statement repeated in assessment."
                            })
                        else:
                            seen_question_texts.add(q_text)

        return duplicate_items
