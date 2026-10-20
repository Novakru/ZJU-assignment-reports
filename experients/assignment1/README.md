# Assignment 1 experiments

Run from the repository root:

```powershell
python -m pip install -r experients/assignment1/requirements.txt
python experients/assignment1/run.py
```

Every question has a standalone script. Each can be run directly, without
importing another question's implementation:

```powershell
python experients/assignment1/q1_vanishing_point.py
python experients/assignment1/q4_rigid_distance.py
```

| Question | Script | Computation |
| --- | --- | --- |
| 1 | `q1_vanishing_point.py` | Exact limits of both projected lines |
| 2 | `q2_vanishing_line.py` | Plane gradient and vanishing-line equation |
| 3 | `q3_plane_normal.py` | Normal proportionality and a basis of tangent directions |
| 4 | `q4_rigid_distance.py` | Symbolic distance identity for arbitrary orthogonal R |
| 5 | `q5_camera.py` | Normalized DLT and unit Frobenius norm |
| 6 | `q6_triangulation.py` | SVD triangulation and two-view reprojection |
| 7 | `q7_essential_matrix.py` | Essential matrix from translation and rotation |
| 8 | `q8_epipolar_line.py` | Image-2 epipolar line and its equation |
| 9 | `q9_reprojection_error.py` | Exact projection, residual, and Euclidean pixel error |
| 10 | `q10_orthographic.py` | Orthographic projection matrix multiplication |

`verify.py` checks the results returned by all ten scripts and independently
checks exact DLT rank/nullspace, reprojection, and geometric identities.
Q4 also uses 100 proper rotations with random seed 1050 as a numerical check
of the symbolic proof. Q7/Q8 check the epipolar equation on 20 projected 3D points.
Numerical thresholds are `1e-12` for algebraic comparisons and `1e-9` px
for reprojection residuals. All assertions use unrounded data.

`run.py` runs Questions 1-10 in numerical order, then runs `verify.py` with
the same Python interpreter. It aborts on failure and captures actual stdout:

| Artifact | Meaning |
| --- | --- |
| `results/q*.txt` | One printed-output file per question, with the same stem as its script |
| `results/verify.txt` | Independent check results |
| `results/manifest.json` | Environment versions and full SHA-256 source/input/output hashes |
| `results/provenance.tex` | Generated environment table embedded in the report |
| `results/build.json` | Written by the PDF build: successful checks and final PDF/manifest hashes |

Each question in the PDF contains **Solution, Python code, Run output**, in
that order. The LaTeX report directly includes each complete `.py` file and
its corresponding `.txt` file. Changing a script and rebuilding updates both
the code listing and its printed output. The `question_runs` field in the
manifest records the question-to-script/output mapping.
`inputs.md` records the source questions and submission notice; the original
PDF/notice remain outside this template repository and are hashed if present.

The recorded environment in `results/manifest.json` gives the versions used
for the checked-in results. `requirements.txt` states compatible dependency
ranges; to reproduce package versions exactly, install those recorded versions.
Floating-point last digits, signed zero, and SVD signs can vary across numerical
libraries without changing the result. Q5 fixes the global camera sign.

Q5 intentionally estimates a general projective camera rather than requiring
a finite pinhole model: the given data uniquely yield an affine camera.
Q6 uses the supplied matrix entry `-6` directly; the baseline is `6/900`,
so depth is `0.4` in the unspecified world units.

Q3 and Q4 retain their mathematical proofs in the report. Their scripts
use exact symbolic algebra; the random checks in `verify.py` supplement those
proofs and do not replace them.
