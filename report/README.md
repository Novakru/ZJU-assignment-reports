# Assignment 2 报告

本分支沿用仓库的浙大技术报告样式，以及 `assignment1-cs1050` 的课程作业版式：浙大横向 Logo、求是蓝、衬线正文与居中页码。增加中文字体支持，章节按本次 MP2 要求组织。未使用示例中的实验室身份或课程1的教师、课程号。

封面统一为 **ECE2013 · Fall 2026 · Group 6**，组员为王骊斌、蒋佳豪、王子征、薛晓康，不列学号。信息集中在 `student-info.tex`。贡献表是供组内分派任务的暂拟方案，明确标为待确认，不能视为实际完成记录。真人实验仍待完成。

真人章节已完整渲染10局记录表、胜率汇总、4幅预留终盘和观察填写项。未录入项用破折号与Pending标记，不能解释成平局或零胜率。真人记录保存到 `experients/assignment2/human_games.json` 后，构建会自动更新表格与棋盘；观察文字分别填入 `human-notes.json` 的 `zh`、`en` 下三个字段。

全局三连扩展已完成12局真实自动实验，X胜5局、O胜5局、平局2局，并逐步回放验证。扩展代码包含在提交的 `uttt.py` 中，默认仍运行必做的首个局部棋盘获胜规则。

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

构建时验证必做与扩展对局，生成两种语言的数据表和图注，分别编译两次，并将中文版 PDF 同步到 `submission/report.pdf`。如需重新运行全部自动实验：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File report/build.ps1 -RunExperiments
```

真人实验：

```powershell
python submission/uttt.py human --games 10 --output experients/assignment2/human_games.json
```

完成后重新构建。运行方法与代码路径仅保留在文档中，不进入报告正文。

单独复现扩展实验：

```powershell
python experients/assignment2/run_extra.py
python experients/assignment2/check_extra.py
```

提交文件也可独立运行扩展模式：

```powershell
python submission/uttt.py extra --games 12 --seed 2013 --output extra_games.json
```

模拟对手补充实验：`python -B experients/assignment2/run_simulated.py`，验证：
`python -B experients/assignment2/check_simulated.py`。固定种子20261106，随机、一步攻防、
深度2搜索各10局，对战深度3自定义O；O实测30胜。全部记录明确标记为非真人，
保存在 `simulated_results.json`，不写入真人日志，也不满足真人对战要求。

Blackboard 只上传 `submission` 内的 `solve.py`、`uttt.py`、`report.pdf`，不提交 LaTeX 源文件和实验日志。
