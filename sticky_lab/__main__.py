"""Checked stdin/report/demo/help delivery; never real filesystem operations."""

import argparse
import json
import sys

from .core import MAX_INPUT_BYTES, analyze_json, evaluate, serialize_report
from .fixtures import oracles

HELP = "usage: sticky_lab {analyze,demo}\n\nSupplied sticky-directory predicates; actual unlink unverified.\n\nanalyze: bounded UTF8 JSON on stdin\ndemo: thirteen independently frozen reports\n--help: this fixed usage text\n"


def _text(destination, message):
    if destination is None:
        raise OSError("absent output stream")
    if destination.write(message) != len(message):
        raise OSError("short text write")
    destination.flush()


class _CheckedParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        _text(sys.stdout if file is None else file, HELP)

    def error(self, message):
        # User argv is never reflected, including escape/control characters.
        _text(sys.stderr, '{"error":"invalid_arguments"}\n')
        raise SystemExit(2)


def _io_failure():
    diagnostic = sys.stderr
    # Dirty buffers must not replace the controlled exit during CPython shutdown.
    sys.stdout = sys.stderr = None
    try:
        _text(diagnostic, '{"error":"input_or_output_failure"}\n')
    except (OSError, ValueError):
        pass
    return 3


def main():
    parser = _CheckedParser(prog="sticky_lab", add_help=True)
    parser.add_argument("command", choices=("analyze", "demo"))
    try:
        args = parser.parse_args()
        if args.command == "analyze":
            if sys.stdin is None:
                raise OSError("absent input stream")
            report = analyze_json(sys.stdin.buffer.read(MAX_INPUT_BYTES + 1))
        else:
            cases = []
            for fixture in oracles():
                result = evaluate(fixture["request"])
                cases.append({"report": result, "expected": fixture["expected"],
                              "passed": result == fixture["expected"]})
            report = {"mode": "invented_sticky_predicates", "actual_unlink": "unverified",
                      "entry_removed": "unverified", "storage_reclaimed": "unverified",
                      "cases": cases, "passed": all(case["passed"] for case in cases)}
        payload = serialize_report(report)
        emitted = json.loads(payload)
        if sys.stdout is None or sys.stdout.buffer.write(payload) != len(payload):
            raise OSError("short or absent report write")
        sys.stdout.buffer.flush()
    except (OSError, ValueError):
        return _io_failure()
    if emitted.get("status") == "over_limit":
        return 2
    if args.command == "demo":
        return 0 if report["passed"] else 1
    if not report["complete"]:
        return 2
    return 0 if report["model_permits_unlink"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
