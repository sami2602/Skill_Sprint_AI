"""
SkillSprint AI — Role Requirement Matrix Builder Engine
Constructs deterministic ground-truth requirement matrices for job roles (including unseen hidden evaluation roles).
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.models import Role, PolicyRequirement, RoleRequirementMapping, Document, RequirementCategoryEnum


class RoleMatrixBuilder:
    """Builds and retrieves the ground-truth Role Requirement Matrix."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def build_matrix_for_role(self, role_id: str) -> Dict[str, Any]:
        """
        Dynamically constructs the requirement matrix for a given role ID.
        Handles both stored database roles and unseen new roles (HE-01).
        """
        role = self.db.query(Role).filter(Role.role_id == role_id).first()

        # Handle unseen new role dynamically if not present in DB
        role_title = role.title if role else role_id.replace("_", " ").title()
        department = role.department if role else "Operations"

        # Query active requirements
        active_docs = self.db.query(Document).filter(Document.is_active == True).all()
        active_doc_ids = [d.id for d in active_docs]
        doc_map = {d.id: d for d in active_docs}

        requirements = self.db.query(PolicyRequirement).filter(
            PolicyRequirement.document_id.in_(active_doc_ids)
        ).all()

        mandatory_items = []
        optional_items = []

        for req in requirements:
            target_roles = req.target_roles or ["ALL"]
            is_applicable = ("ALL" in target_roles) or (role_id in target_roles) or (department.lower() in (req.department or "").lower())

            if not is_applicable:
                continue

            doc = doc_map.get(req.document_id)
            doc_code = doc.doc_id if doc else f"DOC-{req.document_id}"
            doc_version = doc.version if doc else "1.0"

            item_data = {
                "requirement_id": req.requirement_id,
                "title": req.title,
                "requirement_text": req.requirement_text,
                "category": req.category.value if hasattr(req.category, 'value') else str(req.category),
                "is_mandatory": req.is_mandatory,
                "priority": req.priority.value if hasattr(req.priority, 'value') else str(req.priority),
                "source_doc_id": doc_code,
                "source_version": doc_version,
                "source_section_ref": req.section_ref,
                "evidence_citation": f"{doc_code} v{doc_version} ({req.section_ref})"
            }

            if req.is_mandatory:
                mandatory_items.append(item_data)
            else:
                optional_items.append(item_data)

        return {
            "role_id": role_id,
            "role_title": role_title,
            "department": department,
            "mandatory_requirement_count": len(mandatory_items),
            "optional_requirement_count": len(optional_items),
            "total_requirement_count": len(mandatory_items) + len(optional_items),
            "mandatory_items": mandatory_items,
            "optional_items": optional_items
        }

    def get_ground_truth_matrix_summary(self) -> List[Dict[str, Any]]:
        """Returns summary matrix statistics across all configured job roles."""
        roles = self.db.query(Role).all()
        summaries = []
        for r in roles:
            matrix = self.build_matrix_for_role(r.role_id)
            summaries.append({
                "role_id": r.role_id,
                "title": r.title,
                "department": r.department,
                "mandatory_count": matrix["mandatory_requirement_count"],
                "optional_count": matrix["optional_requirement_count"],
                "total_count": matrix["total_requirement_count"]
            })
        return summaries
