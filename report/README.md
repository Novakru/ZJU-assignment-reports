# Assignment 2 报告

本分支沿用仓库的浙大技术报告样式，以及 `assignment1-cs1050` 的课程作业版式：浙大横向 Logo、求是蓝、衬线正文与居中页码。增加中文字体支持，章节按本次 MP2 要求组织。未使用示例中的实验室身份或课程1的教师、课程号。

姓名与学号沿用已有作业分支中的信息，位于 `student-info.tex`；课程号和班级尚未提供，在 `report.tex` 中保留为待补充。真人实验尚未完成，报告中明确留待补充。

在仓库根目录构建（需 XeLaTeX、Python）：

```powershell
python -m pip install -r experients/assignment2/requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File report/build.ps1
```

构建时验证已有对局、生成数据表与矢量棋盘图、编译两次，并将 PDF 同步到 `submission/report.pdf`。如需重新运行全部自动实验：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File report/build.ps1 -RunExperiments
```

真人实验：

```powershell
python submission/uttt.py human --games 10 --output experients/assignment2/human_games.json
```

完成后重新构建。运行方法与代码路径仅保留在文档中，不进入报告正文。

Blackboard 只上传 `submission` 内的 `solve.py`、`uttt.py`、`report.pdf`，不提交 LaTeX 源文件和实验日志。
