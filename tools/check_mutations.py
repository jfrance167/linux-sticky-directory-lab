"""Three in-memory logic faults must cause assertions, then restored tests pass.

Usage: python tools/check_mutations.py. No source edits, commands or network.
Errors do not count as detection; this is not a mutation coverage score.
"""
from io import StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from sticky_lab import core
from test_core import CoreTests


def run_case(name):
    result = unittest.TextTestRunner(stream=StringIO()).run(unittest.TestSuite([CoreTests(name)]))
    return {"passed": result.wasSuccessful(), "assertion_failures": len(result.failures),
            "errors": len(result.errors), "tests_run": result.testsRun,
            "failure_evidence": [detail for _, detail in result.failures],
            "error_evidence": [detail for _, detail in result.errors]}


def main():
    original = core._decide
    def content_fault(data):
        result = original(data)
        result["model_permits_unlink"] = result["model_permits_unlink"] and bool(data[-1] & 2)
        return result
    pairs = (("prerequisite_or", "_parent_pass", lambda write, search: write or search, "test_prerequisite_regression"),
             ("ownership_and", "_owner_pass", lambda parent, target: parent and target, "test_ownership_regression"),
             ("content_misuse", "_decide", content_fault, "test_content_regression"))
    mutations = []
    for name, target, fault, test in pairs:
        with patch.object(core, target, fault):
            result = run_case(test)
        mutations.append({"mutation": name, **result,
                          "detected": result["assertion_failures"] > 0 and result["errors"] == 0})
    restored = [run_case(test) for _, _, _, test in pairs]
    print(json.dumps({"mutations": mutations, "restored": restored,
                      "scope": "three in-memory faults; no source mutation"}, indent=2))
    return 0 if all(item["detected"] for item in mutations) and all(item["passed"] for item in restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
