# Assignment 2 experiments

Run `python experients/assignment2/run.py` from the repository root. Ten standalone scripts cover five Q1 parts and Q2-Q6. Each script contains result assertions; every neural-network forward pass uses actual CPU tensors of the requested size. Q3-Q5 are explicitly limited illustrative examples, not pretrained-model experiments. Q1.5 uses Conv1d along the sequence, since the question requests a convolutional layer without restricting its dimensionality.

The runner captures stdout and hashes sources, inputs, and outputs in results/manifest.json. `report/build.ps1` runs the scripts and compiles the PDF twice. results/build.json records final PDF and manifest hashes. The manifest records the actual dependency versions; requirements.txt specifies compatible ranges. CPU seed is 1050. No model download or GPU is required.

Reference content: PyTorch 2.14 documentation, Mask R-CNN section 3, the official SMPL website, CLIP sections 2.3 and 3.1. URLs appear in the report.

Repository setup: the initial GitHub SSH and HTTPS connections stalled, so the Assignment1 local repository history was fetched into this independent checkout, and branch assignment2-cs1050 was created from e8d67c6. The GitHub origin is retained. Remote freshness has not been confirmed.
