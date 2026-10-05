"""Real CPython shutdown and closed pipes; invented data, no unlink/identity calls.

The help/error launcher waits for an explicit stdin barrier so the parent can
close readers before parser output. Analyze uses its own bounded stdin read.
Timeouts are harness bounds, not application resource containment claims.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
OBSERVED = []
DIAGNOSTIC = b'{"error":"input_or_output_failure"}' + os.linesep.encode("ascii")


def child(args, *, optimized=False, closed=(), barrier=False, fault=None, state=None, raw=b"{}"):
    command = [sys.executable] + (["-O"] if optimized else [])
    if state is not None:
        # Labeled Python-stream seams; native closed pipe coverage is separate.
        launcher = "import sys,runpy; sys.stdin.buffer.read(1);\n"
        for name, action in state:
            launcher += f"sys.{name}.close()\n" if action == "closed" else f"sys.{name}=None\n"
        launcher += f"sys.argv={['sticky_lab', *args]!r}\n"
        launcher += "runpy.run_module('sticky_lab',run_name='__main__')"
        command += ["-c", launcher]
    elif fault is not None:
        # Explicit synthetic stream seams in a real child interpreter. Flush
        # remains dirty unless main detaches the sink before interpreter exit.
        launcher = '''import sys,runpy
class Sink:
    @property
    def buffer(self):
        return self
    def write(self, payload):
        return 0 if SHORT else len(payload)
    def flush(self):
        raise OSError("synthetic dirty flush")
sys.stdin.buffer.read(1)
'''
        launcher += f"SHORT={fault.endswith('short')!r}\n"
        launcher += f"sys.{('stderr' if fault.startswith('stderr') else 'stdout')}=Sink()\n"
        launcher += f"sys.argv={['sticky_lab', *args]!r}\n"
        launcher += "runpy.run_module('sticky_lab',run_name='__main__')"
        command += ["-c", launcher]
    elif barrier:
        launcher = ("import sys,runpy; sys.stdin.buffer.read(1); "
                    f"sys.argv={['sticky_lab', *args]!r}; "
                    "runpy.run_module('sticky_lab',run_name='__main__')")
        command += ["-c", launcher]
    else:
        command += ["-m", "sticky_lab", *args]
    with subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        for name in closed:
            getattr(process, name).close()
            setattr(process, name, None)
        try:
            output, errors = process.communicate(b"x" if barrier or fault or state else raw, timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise
    result = {"args": args, "optimized": optimized, "closed": list(closed),
              "barrier": barrier or fault is not None or state is not None,
              "synthetic_stream_fault": fault, "synthetic_stream_state": state, "exit": process.returncode,
              "stdout": (output or b"").decode("utf-8"), "stderr": (errors or b"").decode("utf-8")}
    OBSERVED.append(result)
    return process.returncode, output or b"", errors or b""


class ProcessTests(unittest.TestCase):
    def test_child_dirty_short_and_flush_seams(self):
        for optimized in (False, True):
            for fault, args in (("stdout_short", ["analyze"]), ("stdout_flush", ["analyze"]),
                                ("stdout_short", ["--help"]), ("stdout_flush", ["--help"]),
                                ("stderr_short", ["invalid"]), ("stderr_flush", ["invalid"])):
                with self.subTest(optimized=optimized, fault=fault, args=args):
                    code, output, errors = child(args, optimized=optimized, fault=fault)
                    self.assertEqual(code, 3)
                    self.assertEqual(output, b"")
                    self.assertEqual(errors, b"" if fault.startswith("stderr") else DIAGNOSTIC)

    def test_analyze_closed_pipes_normal_and_optimized(self):
        for optimized in (False, True):
            for closed in (("stdout", "stderr"), ("stdout",)):
                with self.subTest(optimized=optimized, closed=closed):
                    code, output, errors = child(["analyze"], optimized=optimized, closed=closed)
                    self.assertEqual(code, 3)
                    self.assertEqual(output, b"")
                    self.assertEqual(errors, b"" if "stderr" in closed else DIAGNOSTIC)

    def test_help_and_parser_error_closed_pipes(self):
        for optimized in (False, True):
            for args, closed in ((["--help"], ("stdout", "stderr")),
                                 (["--help"], ("stdout",)), (["invalid"], ("stderr",))):
                with self.subTest(optimized=optimized, args=args, closed=closed):
                    code, output, errors = child(args, optimized=optimized, closed=closed, barrier=True)
                    self.assertEqual(code, 3)
                    self.assertEqual(output, b"")
                    self.assertEqual(errors, b"" if "stderr" in closed else DIAGNOSTIC)

    def test_healthy_help_and_unused_closed_stderr(self):
        for optimized in (False, True):
            code, output, errors = child(["--help"], optimized=optimized)
            self.assertEqual(code, 0)
            self.assertIn(b"usage:", output)
            self.assertEqual(errors, b"")
            code, output, errors = child(["analyze"], optimized=optimized, closed=("stderr",))
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output)["status"], "rejected")
            self.assertEqual(errors, b"")

    def test_healthy_fixed_parser_diagnostic(self):
        for optimized in (False, True):
            code, output, errors = child(["\x1buntrusted\n"], optimized=optimized)
            self.assertEqual(code, 2)
            self.assertEqual(output, b"")
            self.assertEqual(errors, b'{"error":"invalid_arguments"}' + os.linesep.encode("ascii"))

    def test_closed_python_and_absent_stream_seams(self):
        cases = ((["analyze"], (("stdout", "closed"),)),
                 (["invalid"], (("stderr", "closed"),)),
                 (["--help"], (("stdout", "closed"), ("stderr", "closed"))),
                 (["--help"], (("stdout", "absent"),)),
                 (["analyze"], (("stdout", "absent"), ("stderr", "absent"))),
                 (["analyze"], (("stdin", "absent"),)))
        for optimized in (False, True):
            for args, state in cases:
                with self.subTest(optimized=optimized, args=args, state=state):
                    code, output, errors = child(args, optimized=optimized, state=state)
                    self.assertEqual(code, 3)
                    self.assertEqual(output, b"")
                    self.assertEqual(errors, b"" if any(name == "stderr" for name, _ in state) else DIAGNOSTIC)

    def test_healthy_full_reports_and_demo(self):
        from sticky_lab.fixtures import oracles
        for optimized in (False, True):
            for index, expected in ((0, 0), (2, 1)):
                fixture = oracles()[index]
                code, output, errors = child(["analyze"], optimized=optimized,
                                            raw=json.dumps(fixture["request"]).encode())
                self.assertEqual(code, expected)
                self.assertEqual(json.loads(output), fixture["expected"])
                self.assertEqual(errors, b"")
            code, output, errors = child(["demo"], optimized=optimized)
            self.assertEqual(code, 0)
            self.assertTrue(json.loads(output)["passed"])
            self.assertEqual(errors, b"")


if __name__ == "__main__":
    unittest.main()
