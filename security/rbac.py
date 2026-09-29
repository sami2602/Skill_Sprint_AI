"""
SkillSprint AI — Role-Based Access Control (RBAC) & Authorization Engine
Enforces role permissions for Admin, Reviewer, Manager, Training Manager, and Employee (SRS FR-02).
"""

from typing import List, Dict, Any

try:
    from fastapi import HTTPException, status
    class RBACPermissionError(HTTPException):
        def __init__(self, detail: str = "Access denied: insufficient permissions for action."):
            super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
except ImportError:
    class RBACPermissionError(PermissionError):
        def __init__(self, detail: str = "Access denied: insufficient permissions for action."):
            super().__init__(detail)


class RBACManager:
    """Manages role permissions and enforces access authorization rules (FR-02)."""

    ROLE_PERMISSIONS: Dict[str, List[str]] = {
        "ADMIN": [
            "read_all", "write_all", "approve_override", "manage_roles",
            "upload_document", "policy_update", "selective_regenerate", "view_audit"
        ],
        "REVIEWER": [
            "read_all", "approve_override", "review_queue_action",
            "selective_regenerate", "view_audit"
        ],
        "TRAINING_MANAGER": [
            "read_all", "generate_plan", "policy_impact_analyze", "view_audit"
        ],
        "MANAGER": [
            "read_department", "view_employee_dashboard", "view_reports"
        ],
        "EMPLOYEE": [
            "view_own_dashboard", "complete_task", "take_quiz"
        ]
    }

    @classmethod
    def verify_permission(cls, user_role: str, required_permission: str) -> bool:
        """
        Verifies if a user role possesses the required permission.
        Raises RBACPermissionError if unauthorized.
        """
        role_upper = (user_role or "").upper()
        permissions = cls.ROLE_PERMISSIONS.get(role_upper, [])
        if required_permission not in permissions and "write_all" not in permissions:
            raise RBACPermissionError(
                f"Role '{user_role}' is not authorized to perform action requiring '{required_permission}'."
            )
        return True

    @classmethod
    def is_authorized_reviewer(cls, user_role: str) -> bool:
        """Returns True if role is authorized to perform manual reviewer approvals & overrides."""
        role_upper = (user_role or "").upper()
        return role_upper in ["ADMIN", "REVIEWER"]
