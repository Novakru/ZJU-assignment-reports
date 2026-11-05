# Assignment 2 报告

本分支沿用仓库的浙大技术报告样式，以及 `assignment1-cs1050` 的课程作业版式：浙大横向 Logo、求是蓝、衬线正文与居中页码。增加中文字体支持，章节按本次 MP2 要求组织。未使用示例中的实验室身份或课程1的教师、课程号。

封面统一为 **ECE2013 · Fall 2026 · Group 6**，组员为王骊斌、蒋佳豪、王子征、薛晓康，不列学号。信息集中在 `student-info.tex`。贡献表是供组内分派任务的暂拟方案，明确标为待确认，不能视为实际完成记录。真人实验仍待完成。

## 中英文复核版本

- `report.tex` → `report.pdf`：中文版。
- `report-en.tex` → `report-en.pdf`：英文版。

两版共用样式、实验数据与矢量棋盘。表格与图注分别本地化，数值和抽取的代表局面保持一致。当前 `submission/report.pdf` 沿用中文版；英文版留在报告目录供复核，不额外放入仅允许三个文件的提交目录。

报告保留作业指定的章节顺序，在对应章节补充精确覆盖约束、Algorithm X与MRV、minimax递推、α–β剪枝条件，以及评估特征和有限搜索视野。原理与实验结果分别排版，原始结果保持不变。封面使用统一左对齐和衬线学院名称，以留白取代标题与组员信息之间的分隔线。

用户提到的“参考作业”尚未在当前工作目录及相邻课程目录中找到，需补充路径或链接后再核对；本次不能声称已经参考该文件。

在仓库根目录构建（需 XeLaTeX、Python）：

```powershell
python -m pip install -r experients/assignment2/requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File report/build.ps1
```

构建时验证已有对局，生成两种语言的数据表和图注，分别编译两次，并将中文版 PDF 同步到 `submission/report.pdf`。如需重新运行全部自动实验：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File report/build.ps1 -RunExperiments
```

真人实验：

```powershell
python submission/uttt.py human --games 10 --output experients/assignment2/human_games.json
```

完成后重新构建。运行方法与代码路径仅保留在文档中，不进入报告正文。

Blackboard 只上传 `submission` 内的 `solve.py`、`uttt.py`、`report.pdf`，不提交 LaTeX 源文件和实验日志。
