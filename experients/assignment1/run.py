"""Run the experiments and capture real stdout plus SHA-256 provenance."""

import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = HERE / "results"
    output.mkdir(exist_ok=True)
    for script in ("q5_camera.py", "q6_triangulation.py", "verify.py"):
        completed = subprocess.run(
            [sys.executable, str(HERE / script)], cwd=HERE,
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        (output / (Path(script).stem + ".txt")).write_text(
            completed.stdout, encoding="utf-8", newline="\n"
        )
        print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")

    paths = [
        *sorted(HERE.glob("*.py")), HERE / "requirements.txt", HERE / "inputs.md",
        ROOT / ".gitattributes",
        ROOT / "zju-tech-report" / "assets" / "zju-horizontal-blue.png",
        ROOT / "report" / "report.tex", ROOT / "report" / "student-info.tex",
        ROOT / "report" / "assignment.sty", ROOT / "report" / "build.ps1",
        *sorted(output.glob("*.txt")),
    ]
    external_inputs = {}
    for filename in ("assignment1_CS1050.pdf", "任务要求.md"):
        path = ROOT.parent / filename
        if path.exists():
            external_inputs[filename] = sha256(path)
        else:
            external_inputs[filename] = "not present; see inputs.md for transcription"
    manifest = {
        "command": "python experients/assignment1/run.py",
        "environment": {
            "python": platform.python_version(), "numpy": np.__version__,
            "sympy": sp.__version__, "platform": platform.platform(),
        },
        "external_inputs_sha256": external_inputs,
        "files_sha256": {p.relative_to(ROOT).as_posix(): sha256(p) for p in paths},
        "note": "SHA-256 binds these results to source files; it does not assert authorship.",
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
    provenance = [
        r"\begin{tabular}{ll}", r"\toprule", r"Component & Recorded value \\",
        r"\midrule",
        f"Python & {platform.python_version()} " + r"\\",
        f"NumPy & {np.__version__} " + r"\\",
        f"SymPy & {sp.__version__} " + r"\\",
        "Manifest SHA-256 (first 16 hex) & " + r"\texttt{" + sha256(manifest_path)[:16] + r"} \\",
        r"\bottomrule", r"\end{tabular}",
    ]
    (output / "provenance.tex").write_text("\n".join(provenance) + "\n", encoding="utf-8")
    print("Captured stdout and provenance in experients/assignment1/results/.")


if __name__ == "__main__":
    main()
