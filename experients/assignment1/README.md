# Assignment 1 experiments

Run from the repository root:

```powershell
python -m pip install -r experients/assignment1/requirements.txt
python experients/assignment1/run.py
```

`q5_camera.py` and `q6_triangulation.py` are standalone Python submissions:

```powershell
python experients/assignment1/q5_camera.py
python experients/assignment1/q6_triangulation.py
```

`verify.py` independently checks the exact DLT rank/nullspace and reprojection,
the triangulation result, and the other eight answers. Q4 uses 100 proper
rotations with random seed 1050 as an additional numerical check of the proof.
Q7/Q8 also check the epipolar equation on 20 projected 3D points.
Numerical thresholds are `1e-12` for algebraic comparisons and `1e-9` px
for reprojection residuals. All assertions use unrounded data.

`run.py` runs these scripts with the same Python interpreter, aborts on failure,
and captures **actual stdout**, not manually typed sample results:

| Artifact | Meaning |
| --- | --- |
| `results/q5_camera.txt` | Printed Q5 camera, norm, rank, singular values, and reprojection |
| `results/q6_triangulation.txt` | Printed Q6 3D point, singular values, and two-view reprojection |
| `results/verify.txt` | Independent check results |
| `results/manifest.json` | Environment versions and full SHA-256 source/input/output hashes |
| `results/provenance.tex` | Generated environment table embedded in the report |
| `results/build.json` | Written by the PDF build: successful checks and final PDF/manifest hashes |

The LaTeX report directly includes the `.py` and `.txt` files. Thus changing a
script and rebuilding updates both the code listing and its printed output.
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
