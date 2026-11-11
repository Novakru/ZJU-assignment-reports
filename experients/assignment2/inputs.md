# Assignment 2 inputs

Original inputs: `../assignment2_CS1050.pdf` (4 pages) and `../任务要求.md`, relative to repository root. Original bytes are hashed in results/manifest.json.

Deadline: November 27, 2026, 23:59 CST. Submit one PDF, first-page identity, readable equations/code/output.

Q1: Linear (80,640)->(80,320); Conv2d input (20,36,224,160), targets (20,48,111,79), (20,72,112,161), (20,72,112,53) with kernel/stride/padding/dilation/groups as shown in report; RNN (28,20,96), 4 layers, hidden 192; Transformer (80,24,384), 6 heads, batch first; combined architecture input/output (64,24,384), all four components, 6 heads, batch first.

Q2: A=[[0,1,1],[1,0,1],[1,1,0]], X=[[1,2],[2,1],[0,1]], W=[[2,1],[0,1]]. Add I, use symmetric degree normalization, identity activation.

Q3: ROI Align versus ROI Pooling for instance segmentation.
Q4: SMPL and the meanings of theta and beta.
Q5: CLIP training objective, mechanism, zero-shot classification.
Q6: A->B reward -3, B->D reward +12; gamma=0.8; V(D)=0.
