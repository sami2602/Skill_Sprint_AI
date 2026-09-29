"""
SkillSprint AI — Phase 2 Master Test Runner
Executes dataset seeding, dataset ground-truth validation, and Pytest test suite for Phase 2.
"""

import os
import sys
import subprocess


def run_phase2_suite():
    print("==================================================================")
    print("   SKILLSPRINT AI — PHASE 2 VERIFICATION SUITE (PYTHON 3.14.7)   ")
    print("==================================================================")

    print("\n[Step 1/3] Executing Dataset Seeding Script...")
    seed_res = subprocess.run([sys.executable, "scripts/seed_dataset.py"])
    if seed_res.returncode != 0:
        print("ERROR: Dataset seeding failed!")
        return sys.exit(1)

    print("\n[Step 2/3] Executing Ground-Truth Dataset Validation...")
    val_res = subprocess.run([sys.executable, "scripts/validate_dataset.py"])
    if val_res.returncode != 0:
        print("ERROR: Dataset ground-truth validation failed!")
        return sys.exit(1)

    print("\n[Step 3/3] Executing Pytest Test Suite for Phase 2...")
    pytest_res = subprocess.run([sys.executable, "-m", "pytest", "tests/unit", "tests/integration", "-v"])
    if pytest_res.returncode != 0:
        print("ERROR: Pytest test suite failed!")
        return sys.exit(1)

    print("\n==================================================================")
    print("   ALL PHASE 2 VERIFICATION STEPS PASSED SUCCESSFULLY (100%)      ")
    print("==================================================================")


if __name__ == "__main__":
    run_phase2_suite()
