"""Run the experiments and capture real stdout plus SHA-256 provenance."""

import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp
import torch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QUESTIONS = (
    "q1_1_linear", "q1_2_convolution", "q1_3_rnn",
    "q1_4_transformer", "q1_5_network", "q2_gcn", "q3_roi_align",
    "q4_smpl", "q5_clip", "q6_values",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = HERE / "results"
    output.mkdir(exist_ok=True)
    for name in (*QUESTIONS, "verify"):
        script = name + ".py"
        completed = subprocess.run(
            [sys.executable, str(HERE / script)], cwd=HERE,
            capture_output=True, text=True, encoding="utf-8",
        )
        if completed.returncode:
            print(completed.stdout, end="")
            print(completed.stderr, file=sys.stderr, end="")
            completed.check_returncode()
        (output / (Path(script).stem + ".txt")).write_text(
            completed.stdout, encoding="utf-8", newline="\n"
        )
        print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")

    paths = [
        *sorted(HERE.glob("*.py")), HERE / "requirements.txt", HERE / "inputs.md",
        ROOT / ".gitattributes",
        ROOT / "report" / "assets" / "zjui-horizontal-color.pdf",
        ROOT / "report" / "report.tex", ROOT / "report" / "student-info.tex",
        ROOT / "report" / "assignment.sty", ROOT / "report" / "build.ps1",
        *sorted(output.glob("*.txt")),
    ]
    external_inputs = {}
    for filename in ("assignment2_CS1050.pdf", "任务要求.md"):
        path = ROOT.parent / filename
        if path.exists():
            external_inputs[filename] = sha256(path)
        else:
            external_inputs[filename] = "not present; see inputs.md for transcription"
    manifest = {
        "command": "python experients/assignment2/run.py",
        "environment": {
            "python": platform.python_version(), "numpy": np.__version__,
            "sympy": sp.__version__, "torch": torch.__version__,
            "platform": platform.platform(),
        },
        "question_runs": [
            {"question": name.split("_")[0], "source": name + ".py", "stdout": "results/" + name + ".txt"}
            for i, name in enumerate(QUESTIONS, 1)
        ],
        "external_inputs_sha256": external_inputs,
        "files_sha256": {p.relative_to(ROOT).as_posix(): sha256(p) for p in paths},
        "note": "SHA-256 records source, input, and output file versions.",
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
        f"PyTorch (CPU) & {torch.__version__} " + r"\\",
        "Manifest SHA-256 (first 16 hex) & " + r"\texttt{" + sha256(manifest_path)[:16] + r"} \\",
        r"\bottomrule", r"\end{tabular}",
    ]
    (output / "provenance.tex").write_text("\n".join(provenance) + "\n", encoding="utf-8")
    print("Captured stdout and provenance in experients/assignment2/results/.")


if __name__ == "__main__":
    main()
