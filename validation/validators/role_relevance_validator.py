"""
SkillSprint AI — Role Relevance Validator
Verifies that generated content is relevant to the target job role and department, flagging inappropriate cross-role requirements.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.models import Role, PolicyRequirement


class RoleRelevanceValidator:
    """Validates role applicability and flags cross-role irrelevancies (FR-39)."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def validate(self, role_id: str, plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans generated content for items mapped to requirements intended strictly for other job roles.
        Returns list of role_irrelevance_flags.
        """
        role_irrelevance_flags: List[Dict[str, Any]] = []

        role = self.db.query(Role).filter(Role.role_id == role_id).first()
        dept = (role.department if role else "Operations").lower()

        all_reqs = {r.requirement_id: r for r in self.db.query(PolicyRequirement).all()}

        modules = plan_data.get("modules", [])
        for mod in modules:
            mod_id = mod.get("module_id", "MOD-UNKNOWN")
            mod_title = mod.get("title", "Untitled Module")

            for rm in mod.get("requirement_mappings", []):
                req_id = rm.get("requirement_id") if isinstance(rm, dict) else getattr(rm, "requirement_id", None)
                if req_id and req_id in all_reqs:
                    req = all_reqs[req_id]
                    t_roles = req.target_roles or ["ALL"]
                    is_role_match = ("ALL" in t_roles) or (role_id in t_roles) or (dept in (req.department or "").lower())

                    if not is_role_match:
                        role_irrelevance_flags.append({
                            "item_id": mod_id,
                            "item_type": "MODULE",
                            "title": mod_title,
                            "requirement_id": req_id,
                            "target_roles": t_roles,
                            "assigned_role": role_id,
                            "reason": f"Module maps to requirement '{req_id}' targeted for roles {t_roles}, not assigned role '{role_id}'.",
                            "evidence": f"Requirement '{req_id}' is role-specific to {t_roles}."
                        })

            for task in mod.get("tasks", []):
                task_id = task.get("task_id", "TSK-UNKNOWN")
                task_title = task.get("title", "Untitled Task")

                for rm in task.get("requirement_mappings", []):
                    req_id = rm.get("requirement_id") if isinstance(rm, dict) else getattr(rm, "requirement_id", None)
                    if req_id and req_id in all_reqs:
                        req = all_reqs[req_id]
                        t_roles = req.target_roles or ["ALL"]
                        is_role_match = ("ALL" in t_roles) or (role_id in t_roles) or (dept in (req.department or "").lower())

                        if not is_role_match:
                            role_irrelevance_flags.append({
                                "item_id": task_id,
                                "item_type": "TASK",
                                "title": task_title,
                                "requirement_id": req_id,
                                "target_roles": t_roles,
                                "assigned_role": role_id,
                                "reason": f"Task maps to requirement '{req_id}' targeted for roles {t_roles}, not assigned role '{role_id}'.",
                                "evidence": f"Requirement '{req_id}' is role-specific to {t_roles}."
                            })

        return role_irrelevance_flags
