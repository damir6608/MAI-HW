"""Run the demo, all tests and the controlled before/after comparison."""

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    """Save real subprocess output and a machine-readable summary."""
    root = Path(__file__).resolve().parent
    demo = root / "foodtech_demo"
    evidence = root / "evidence"
    evidence.mkdir(exist_ok=True)
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.pop("PRICING_VARIANT", None)
    summary = {"verified_at_utc": datetime.now(timezone.utc).isoformat()}
    commands = [
        ("demo", ["demo.py"], None),
        ("tests", ["-m", "unittest", "discover", "-s", "tests", "-v"], None),
        ("before", ["-m", "unittest", "tests.test_pricing", "-v"], "before.py"),
        ("after", ["-m", "unittest", "tests.test_pricing", "-v"], "after.py"),
    ]
    for name, arguments, variant in commands:
        local_env = environment.copy()
        if variant:
            local_env["PRICING_VARIANT"] = str(root / "ДЗ2" / "experiments" / variant)
        process = subprocess.run(
            [sys.executable, *arguments], cwd=demo, env=local_env,
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        output = process.stdout + process.stderr
        (evidence / f"{name}.txt").write_text(output, encoding="utf-8")
        summary[name] = {"exit_code": process.returncode, "log": f"{name}.txt"}
        print(f"{name}: exit_code={process.returncode}")

    codex = shutil.which("codex")
    codex_version = "not found"
    if codex:
        process = subprocess.run(
            [codex, "--version"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=False,
        )
        codex_version = process.stdout.strip()
        (evidence / "codex_version.txt").write_text(
            process.stdout + process.stderr, encoding="utf-8",
        )
    summary["environment"] = {
        "python": platform.python_version(), "platform": platform.system(),
        "codex_version": codex_version,
        "external_python_dependencies": 0,
    }
    (evidence / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    if summary["demo"]["exit_code"] or summary["tests"]["exit_code"]:
        raise SystemExit(1)
    if summary["after"]["exit_code"] or summary["before"]["exit_code"] != 1:
        raise SystemExit("unexpected comparison result; inspect evidence")


if __name__ == "__main__":
    main()
