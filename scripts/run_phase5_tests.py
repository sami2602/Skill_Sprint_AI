"""
SkillSprint AI — Phase 5 Test & Verification Runner Script
Executes all Phase 5 unit, integration, and security tests, and runs validation benchmarks.
"""

import os
import sys
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.run_phase5_validation_benchmark import run_benchmark


def main():
    print("=" * 70)
    print("  SkillSprint AI — Phase 5 Test Suite Runner")
    print("=" * 70)

    # 1. Run Pytest Suite
    print("\n[1/2] Running Pytest Unit, Integration, and Security Tests...")
    exit_code = pytest.main([
        "-v",
        "tests/unit/test_python_validation.py",
        "tests/unit/test_comparison_engine.py",
        "tests/unit/test_review_queue.py",
        "tests/security/test_adversarial_validator.py",
        "tests/integration/test_validation_pipeline.py"
    ])

    if exit_code != 0:
        print(f"\n❌ Phase 5 Pytest execution failed with code {exit_code}")
        sys.exit(exit_code)

    # 2. Run Benchmark
    print("\n[2/2] Running Phase 5 Performance Benchmark...")
    run_benchmark()

    print("\n[SUCCESS] PHASE 5 COMPLETE & VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
