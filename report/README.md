# Assignment 2 报告

本分支沿用仓库的技术报告样式：求是蓝、衬线正文与居中页码。封面改用ZJUI官方彩色组合标识与居中学术报告版式；中文字体与章节按本次 MP2 要求组织。未使用示例中的实验室身份或课程1的教师、课程号。

封面课程为 **ECE2013: AI Theory and Application · Section 1149-LEC · Fall 2026**，作业小组为 **Group 6**。组员为王骊斌、蒋佳豪、王子征、薛晓康，不列学号。信息集中在 `student-info.tex`。贡献表为组内已确认的实际分工。

真人章节已录入12局、胜率汇总、4幅代表终盘及分析。真人记录位于 `experients/assignment2/human_games.json`，观察文字位于 `human-notes.json` 的 `zh`、`en` 下三个字段。

全局三连扩展已完成12局真实自动实验，X胜5局、O胜5局、平局2局，并逐步回放验证。扩展代码包含在提交的 `uttt.py` 中，默认仍运行必做的首个局部棋盘获胜规则。

## 中英文复核版本

- `report.tex` → `report.pdf`：中文版。
- `report-en.tex` → `report-en.pdf`：英文版。

两版共用样式、实验数据与矢量棋盘。表格与图注分别本地化，数值和代表局面保持一致。`submission/report.pdf` 使用英文版；中文版用于复核，不额外放入仅允许三个文件的提交目录。

报告保留作业指定的章节顺序，在对应章节补充精确覆盖约束、Algorithm X与MRV、minimax递推、α–β剪枝条件，以及评估特征和有限搜索视野。原理与实验结果分别排版，原始结果保持不变。封面以学院标识、课程信息、报告题名、组员和日期构成单一居中轴线。课程名称18pt，课程号、教学班与学期紧接下一行集中排版；标题32pt，作业编号、组号及姓名16pt，副标题与日期14pt。

封面标识来自学院官网的 [ZJUI视觉规范](https://zjui.intl.zju.edu.cn/sites/default/files/2023-02/ZJUI%20VI.pdf)，
采用第1页彩色横向组合，保持官方图形、字形、颜色和比例，以矢量PDF保存于
`assets/zjui-horizontal-color.pdf`。提取区域为原PDF坐标 `(128, 90, 454, 149)`，
只裁去样张外围留白，不重绘或重新排字。标识权利归相应机构所有。
版式参考 [UIUC GE494标题页示例](https://courses.grainger.illinois.edu/ge494/documents/sample-titlepage.pdf)
的居中信息块，以及 [UNSW工程报告写作指南](https://www.unsw.edu.au/engineering/sites/default/files/documents/Report_Writing_Guide_for_Engineers_2018ed.pdf)
关于简洁题名页与信息完整性的原则；不照搬其他课程的身份或提交要求。

用户提到的“参考作业”尚未在当前工作目录及相邻课程目录中找到，需补充路径或链接后再核对；本次不能声称已经参考该文件。

在仓库根目录构建（需 XeLaTeX、Python）：

```powershell
python -m pip install -r experients/assignment2/requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File report/build.ps1
```

构建时验证必做与扩展对局，生成两种语言的数据表和图注，分别编译两次，并将英文版 PDF 同步到 `submission/report.pdf`。如需重新运行全部自动实验：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File report/build.ps1 -RunExperiments
```

真人实验（图形界面）：双击仓库根目录的 `play_human.cmd`，或运行
`python -B tools/play_gui.py`。点击高亮空格落子，真人执X，深度3自定义智能体执O。
完整对局立即保存至真人日志，可分次累计；退出时未完成的当前局不计入结果。
可继续完成超过10局。点击“更新中英文报告”重新构建；若在当前课程目录使用，
还会同步外层 `submission` 与 `review`。图形程序仅使用标准库Tkinter，
不加入仅允许三个文件的提交目录。验证命令：`python -B tools/check_gui.py`，
自动点击测试只写临时文件，不会录入正式真人数据。

也可保留使用命令行真人实验：

```powershell
python submission/uttt.py human --games 10 --output experients/assignment2/human_games.json
```

完成后重新构建。`python -B experients/assignment2/check_human.py` 会逐步验证真人日志：
落点、终盘、独立三连判定，以及智能体每一步的选择、估值和节点数。
当前12局真人实验为真人2胜、智能体10胜、无平局；代表图包含第1、2、6、8局，
观察文字依据记录与倒数第二手的合法选择枚举填写。
真人实验共12局，智能体搜索深度为3；四层、五层对照数据来自自动对战。
运行方法与代码路径仅保留在文档中，不进入报告正文。

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

报告包含扩展规则下自定义进攻X与自定义防守O的搜索深度对照（90局），
以及三层四组预定义对局、40局自定义对攻及12局真人结果。
以下为实验日志与脚本的复现信息。

已完成的深度对照保留全部原有三层结果和提交代码默认深度，评估权重均不变：

- 基础版：预定义进攻X对自定义O，`(dX,dO)` 为 `(3,3)`、`(3,4)`、`(3,5)`、`(4,4)`、`(5,5)`。
- 扩展版：原自定义进攻X对防守O，使用同样五组配置。
- 每组穷举9个起点和2种先手，共18局；两种规则合计180局。
- 另补充四组预定义Minimax/α–β对局的四层与五层版本，共8局。
- 参考耗时在批量实验结束后顺序重测，固定棋盘0、X先手，每配置一次；节点均值使用全部18局。

运行 `python -B experients/assignment2/run_depth.py local` 和同命令的 `global` 模式。
两者完成后运行 `python -B experients/assignment2/time_depth.py`；另运行
`python -B experients/assignment2/run_predefined_depth.py`。记录可断点续跑，已有配置不覆盖。
检查命令为 `python -B experients/assignment2/check_depth.py`，会验证完整配置、
逐步轨迹、三层基线一致性、四/五层搜索等价性，以及真人日志哈希未变。
批量实验支持 `--workers 3` 按独立对局并行；表内参考耗时使用后续顺序重测，
不把并行批次的耗时与顺序耗时混比。188局正式对照外，另有10次参考计时重跑。

以同一18种开局比较，固定X三层时：基础版O的三/四/五层胜率为100%、61.1%、88.9%；
扩展版对应33.3%、61.1%、72.2%。双方同为四层、五层时，基础版O胜率100%、77.8%，
扩展版22.2%、27.8%。扩展版五层同深度有9局平局，O不败率77.8%，不能只用胜率评价。

CSP另有三种搜索策略的节点对照，不报告耗时。调用方式：

```python
from solve import solve, solve_backtracking, solve_forward_checking, solve_algorithm_x
solution = solve(board, tiles)  # Default Algorithm X + MRV; original interface retained.
solution = solve(board, tiles, method='backtracking')
solution = solve_forward_checking(board, tiles)
solution = solve_algorithm_x(board, tiles)
stats = dict(solve.last_stats)
```

三种方法共用候选生成、候选顺序和冲突过滤：BT固定选择首个空格；FC额外检查全部
未满足约束是否出现零候选；AX选择最小候选域。节点为递归调用次数，含根与成功叶，
不含预处理；对照统一使用100万节点上限，触及上限抛出 `SearchLimitReached`，
不会返回“无解”。默认调用没有上限，显式实验可传 `node_limit=1000000`。
状态与候选数、节点数均从 `solve.last_stats` 读取，包装入口也更新同一统计位置。
复现：`python -B experients/assignment2/run_csp_comparison.py`；验证：
`python -B experients/assignment2/check_csp_comparison.py`。共12实例×3策略，
上限内完成数BT为9、FC为11、AX为12；已完成解均通过课程验证器。
比较的是固定候选表示下的搜索策略，而不是独立实现的运行速度。
