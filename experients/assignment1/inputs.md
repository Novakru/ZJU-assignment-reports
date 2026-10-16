# Assignment 1 inputs and requirements

Source: `../assignment1_CS1050.pdf` relative to the repository root (two pages),
and `../任务要求.md`. The runner hashes the originals when available. This file
allows reproduction after cloning the assignment branch without the originals.

Course: Embodied Artificial Intelligence (CS1050), Professor Gaoang Wang,
ZJU--UIUC Institute, October 2026.

## Submission requirements from the notice

- Complete all questions.
- Deadline: October 30, 2026, 23:59, China Standard Time.
- Upload a **single PDF** to Blackboard.
- Put name and student ID on the first page.
- For Python questions, include code and printed results in the PDF.
- Equations, calculations, and code must be clearly readable.
- The question statements additionally request Python code files for Q5 and Q6;
  these are retained here, and their full content is embedded in the PDF.

## Inputs by question

1. `Q(lambda)=(3,1,6)+lambda*(4,2,5)` and
   `R(lambda)=(7,4,2)+lambda*(4,2,5)`; normalized perspective `x=X/Z, y=Y/Z`.
2. Plane `6X+3Y+2Z=17`; same normalized perspective.
3. Show `(3,2,7)` is perpendicular to `12X+8Y+28Z=23`.
4. `x2=R*x1+t`, `y2=R*y1+t`, rotation `R`, `t=(-3,2,1)^T`;
   show Euclidean distance is preserved.
5. Correspondences are **columns**, not rows:

   ```text
   WORLD = [[0,   1,   0,   1,   0.5, 0.5],
            [0,   0,   1,   1,   0.5, 0  ],
            [2,   2,   2,   2,   4,   4  ]]
   IMAGE = [[280, 460, 280, 460, 370, 370],
            [220, 220, 400, 400, 310, 220]]
   ```

   Estimate a `3x4` camera matrix in Python and normalize to Frobenius norm 1.
6. Triangulate in Python:

   ```text
   P1 = [[900, 0,   400,  0],
         [0,   900, 250,  0],
         [0,   0,   1,    0]]
   P2 = [[900, 0,   400, -6],
         [0,   900, 250,  0],
         [0,   0,   1,    0]]
   pixel1 = (400, 250)
   pixel2 = (385, 250)
   ```

7. Calibrated cameras with `K=I`, `R=I`, `t=(3,0,0)^T`;
   convention `X2=R*X1+t`. Find essential matrix `E`.
8. Same setup; first-image homogeneous point `(280,200,1)^T`;
   find the epipolar line **in image 2**.
9. `P=[I|0]`, homogeneous 3D point `(3,1,2,1)^T`, measured
   pixel `(280,200)`. Find Euclidean reprojection error in pixels using
   the matrix as stated; no further calibration is supplied.
10. Orthographic camera at origin, looking along `+Z`, no translation,
    unit scale; project `(5,4,8)^T`.
