"""
SkillSprint AI — Sequence & Prerequisite Validator
Validates stage ordering, prerequisite module/task relationships, and compliance training sequencing.
"""

from typing import List, Dict, Any

STAGE_ORDER = {
    "preboarding": 0,
    "day 1": 1,
    "week 1": 2,
    "week 2": 3,
    "month 1": 4,
    "month 2+": 5,
    "first 30 days": 4,
    "first 60 days": 5,
    "first 90 days": 6
}


class SequenceValidator:
    """Validates onboarding sequence logic and prerequisite dependencies."""

    def validate(self, plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans modules and tasks for stage order and prerequisite violations.
        Returns list of sequence_errors.
        """
        sequence_errors: List[Dict[str, Any]] = []

        modules = plan_data.get("modules", [])
        module_stage_map: Dict[str, int] = {}
        task_stage_map: Dict[str, int] = {}
        task_module_map: Dict[str, str] = {}
        task_mandatory_map: Dict[str, bool] = {}
        module_category_map: Dict[str, str] = {}

        # 1. Map modules and tasks to their stage indices
        for idx, mod in enumerate(modules):
            mod_id = mod.get("module_id", f"MOD-{idx}")
            stage_str = str(mod.get("stage", "Day 1")).lower().strip()
            stage_idx = STAGE_ORDER.get(stage_str, 1)
            module_stage_map[mod_id] = stage_idx

            for task in mod.get("tasks", []):
                task_id = task.get("task_id", "")
                due_stage = str(task.get("due_stage", stage_str)).lower().strip()
                t_stage_idx = STAGE_ORDER.get(due_stage, stage_idx)

                if task_id:
                    task_stage_map[task_id] = t_stage_idx
                    task_module_map[task_id] = mod_id
                    task_mandatory_map[task_id] = task.get("is_mandatory", True)

        # 2. Check module prerequisites
        for mod in modules:
            mod_id = mod.get("module_id", "")
            mod_title = mod.get("title", "")
            current_stage = module_stage_map.get(mod_id, 1)
            prereqs = mod.get("prerequisites", [])

            for prereq_id in prereqs:
                if prereq_id in module_stage_map:
                    prereq_stage = module_stage_map[prereq_id]
                    if prereq_stage > current_stage:
                        sequence_errors.append({
                            "affected_item": mod_id,
                            "item_type": "MODULE",
                            "title": mod_title,
                            "expected_order": f"Prerequisite module '{prereq_id}' scheduled in stage <= {current_stage}",
                            "actual_order": f"Prerequisite module '{prereq_id}' scheduled in stage {prereq_stage} after dependent module '{mod_id}' (stage {current_stage})",
                            "reason": f"Module '{mod_id}' requires prerequisite '{prereq_id}' which is placed in a later stage."
                        })

        # 3. Check task prerequisites
        for mod in modules:
            for task in mod.get("tasks", []):
                task_id = task.get("task_id", "")
                task_title = task.get("title", "")
                current_task_stage = task_stage_map.get(task_id, 1)
                prereq_task_ids = task.get("prerequisite_task_ids", [])

                for p_id in prereq_task_ids:
                    if p_id in task_stage_map:
                        p_stage = task_stage_map[p_id]
                        if p_stage > current_task_stage:
                            sequence_errors.append({
                                "affected_item": task_id,
                                "item_type": "TASK",
                                "title": task_title,
                                "expected_order": f"Prerequisite task '{p_id}' scheduled before dependent task '{task_id}'",
                                "actual_order": f"Prerequisite task '{p_id}' (stage {p_stage}) placed after dependent task '{task_id}' (stage {current_task_stage})",
                                "reason": f"Task '{task_id}' requires prerequisite task '{p_id}' which is placed in a later stage."
                            })

        # 4. Check compliance training sequencing (e.g. Mandatory security/compliance training must be in Preboarding / Day 1)
        for mod in modules:
            mod_title = mod.get("title", "").lower()
            mod_stage = module_stage_map.get(mod.get("module_id"), 1)

            # If module is explicitly security / compliance training but placed in Month 2+ while operational tasks are in Day 1
            if ("security" in mod_title or "compliance" in mod_title or "code of conduct" in mod_title):
                if mod_stage >= STAGE_ORDER.get("month 1", 4):
                    sequence_errors.append({
                        "affected_item": mod.get("module_id", ""),
                        "item_type": "MODULE",
                        "title": mod.get("title", ""),
                        "expected_order": "Mandatory compliance/security training scheduled in Preboarding, Day 1, or Week 1",
                        "actual_order": f"Compliance training '{mod.get('title')}' deferred to Stage {mod_stage} (Month 1+)",
                        "reason": "Mandatory compliance training must precede dependent workplace activities."
                    })

        return sequence_errors
