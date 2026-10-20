# CS1050 Assignment 1 report

本作业位于分支 `assignment1-cs1050`。正文沿用题目的英文，每题统一为：
**Solution（解题过程）→ Python code（完整代码）→ Run output（实际运行输出）**。
10 题均有独立、可直接运行的 Python 脚本，代码与输出放在对应题目下。
证明题保留一般性的数学推导，并使用 SymPy 作符号核验。
排版由 `zju-tech-report/zju-tech-report.tex` 改造：保留浙大标志、求是蓝和
衬线字体，改为课程作业标题、首页姓名/学号、题号、代码列表及打印结果。

## 文件

- `report.tex`：10 题的解题过程、完整 Python 代码和运行输出。
- `assignment.sty`：可复用的课程作业排版。
- `student-info.tex`：已填写 Jiang Jiahao / 22671064；修改后需重新构建。
- `report.pdf`：编译后的单个提交文件。
- `build.ps1`：运行实验、验证并使用 XeLaTeX 编译两次。
- `../experients/assignment1/`：实现、输入说明、真实输出和 SHA-256 追溯记录。

## 编译

需要 Python、NumPy、SymPy 和可用的 XeLaTeX（TeX Live），从仓库根目录运行：

```powershell
python -m pip install -r experients/assignment1/requirements.txt
powershell -NoProfile -File report/build.ps1
```

也可手动执行：

```powershell
python experients/assignment1/run.py
Set-Location report
xelatex -interaction=nonstopmode -halt-on-error report.tex
xelatex -interaction=nonstopmode -halt-on-error report.tex
```

`report.tex` 直接引入实验代码和捕获的打印输出，避免报告与实现分离。
每题从新页开始，较长题目允许跨页；页眉显示当前题号。
运行输出保持为完整区块，代码与输出使用 9 pt 等宽字体。
运行记录含原作业/通知（存在时）、源代码、报告源文件与输出的完整哈希。
修改姓名/学号或正文后应重新运行构建脚本，使追溯记录与 PDF 同步。
构建脚本还会检查最终 LaTeX 日志中的溢出、字体和引用警告，并将最终
PDF 与实验清单的 SHA-256 写入 `experients/assignment1/results/build.json`。

## 提交前

1. 核对 `student-info.tex` 中的姓名和学号；如有修改，重新编译。
2. 核对 `report.pdf` 内容，按课程规定确认解答和辅助工具的使用。
3. 在 2026-10-30 23:59（中国标准时间）之前向 Blackboard 上传该单个 PDF。
   PDF 已逐题收录全部 10 题的完整代码和实际打印结果；独立 `.py` 文件也保存在仓库中。

## 后续作业分支

本分支未更改原技术报告示例。下一次作业可以从 `main` 新建
`assignment2-cs1050`，复制本分支的 `assignment.sty` 等排版基础，另写题目与实验。
切换分支前请先提交或保存当前修改；只有已提交的文件才会随分支保存。
