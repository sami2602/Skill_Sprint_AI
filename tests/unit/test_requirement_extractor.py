"""
SkillSprint AI — Unit Tests for Rule-Based Requirement Extractor
"""

import pytest
from knowledge.requirements.extractor import RuleBasedRequirementExtractor


def test_extractor_mandatory_verbs():
    extractor = RuleBasedRequirementExtractor()
    text = "All employees must encrypt laptop storage. Developers shall follow secure coding standards."
    reqs = extractor.extract_from_chunk("CHK-01", "DOC-POL01", "SEC-01", text)

    assert len(reqs) == 2
    assert reqs[0].is_mandatory is True
    assert reqs[0].modal_verb == "must"
    assert reqs[1].is_mandatory is True
    assert reqs[1].modal_verb == "shall"


def test_extractor_recommended_and_optional_verbs():
    extractor = RuleBasedRequirementExtractor()
    text = "Employees should update passwords quarterly. Staff may request remote work approval."
    reqs = extractor.extract_from_chunk("CHK-02", "DOC-POL02", "SEC-02", text)

    assert len(reqs) == 2
    assert reqs[0].is_mandatory is False
    assert reqs[0].category == "RECOMMENDED"
    assert reqs[1].is_mandatory is False
    assert reqs[1].category == "OPTIONAL"
