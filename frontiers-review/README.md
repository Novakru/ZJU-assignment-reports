# 工程技术前沿：多智能体科研综述

分支 `assignment-engineering-frontiers-review` 从 `main` 建立。
个人课程作业，作者蒋佳豪，学号22671064；不继承MP2的课程号、小组信息、代码或实验。

## 当前稿件

题目：**面向科研任务的多智能体系统综述：技术脉络、关键方法与可信评价**。

正文按引言、研究对象、知识与记忆、分工与检查、科研路径、实证分析、讨论、结语组织，
结合真实综述的组织方式完成学术语言修订，问题背景、方法总结与本文理解融入相应章节。
含中英文题名与摘要、6幅图、4张表，32篇学术报告；工具出处另存于仓库记录。
学术报告包含3篇综述，并明确标注同一项目不同版本之间的关系，不视为独立重复验证。
正文约9400汉字，排除摘要、标题、图表、公式及参考文献，篇幅按完整综述组织。
没有虚构新实验、论文录用、人工核阅或跨系统胜率排名。

稳定预览：`output/pdf/multi-agent-literature-review.pdf`。
个人命名文件：`output/pdf/蒋佳豪22671064.pdf`。
构建后同步到课程目录 `review/`，并将个人命名PDF单独复制到课程目录 `submission/`。
阅读指南与排版样稿保留在 `review/`，不混入 `submission/`。

这是使用AI辅助整理、写作和绘图的课程论文。按作者要求，PDF删除文末资料与工具说明，页脚改为“工程技术前沿课程论文”。
工具出处与处理记录保存在 `tool-provenance.json` 和本仓库的研究记录中。
技术完成不代表作者已确认科学判断或满足课程对AI使用的要求，未上传教学平台。

## 期刊模板及ZJUI适配

采用[《自动化学报》官网LaTeX模板](https://www.aas.net.cn/news/wjxz/37365181-f527-4227-8fa2-b4ce2efd0a3a.htm)
中的2026-09-09版 `aas.cls` 和 `picins.sty`，两个原文件保持原样。
已先编译官方原始示例确认兼容，再由 `journal-review.sty` 单独适配。

保留双栏、学术标题层级、编号引用及三线表；正文调整到11pt，加入ZJUI矢量标识、课程及个人信息。
期刊刊名、卷期、收录号、收稿日期和示例基金等发表元数据均不写入课程报告。
这不是《自动化学报》发表文章，也不是学校官方指定课程模板。
官方模板来源、下载时间和哈希见 `template-source.json`。

标识来自[ZJUI视觉规范](https://zjui.intl.zju.edu.cn/sites/default/files/2023-02/ZJUI%20VI.pdf)，
原PDF第1页横向彩色组合，裁切范围 `(128,90,454,149)`，保持比例与颜色。
标识及上游模板的权利仍归各自权利人，不作额外授权声明。

## 证据与图表

- `review-sources.json`：32篇学术报告的全文链接、版本、页数及SHA256。
- `evidence-extraction.csv`：提取定位、在综述中的用途及边界。
- `research-notes.md`：叙述综述范围、本轮实际查询和防误读记录。
- `data/`：从原文表格逐项提取的数字，未将不同论文的分数合并排名。
- `make_review_diagrams.py`、`figure-provenance.json`：矢量图组、数据重绘与许可面板提取记录。
- `reference-records.tex`、`format_references.py`：书目记录及按首次引用排序的构建脚本，正文引用自动排序、压缩。

图组包括时间分布、检索索引、真实系统架构及装置、产物谱图、科学任务评测和过程审计。
通用的总框架、协作拓扑和研究闭环图已删除；数值图采用黑白与不同点形编码，不用装饰配色。
两个数值图来自ScienceAgentBench固定v3表3和Luo等固定v2表11，图注说明模型、指标、样本及限制。
转载Boiko等Coscientist论文原图1和5i、5j，依据CC BY 4.0保留架构、照片、原坐标、曲线和数值，仅提取面板并重新排列。
原PDF对应页面已打开核对，未添加无来源的误差条。完整论文只在忽略的 `cache/` 本地阅读，不打包提交、不上传Git。

已安装并参考K-Dense的 `literature-review`、`scientific-writing` 和 `scientific-visualization`。
工具论文出处保存在 `tool-provenance.json`，不计入PDF的32篇学术报告；这些技能不是Nature官方技能。
详见 `research-notes.md` 的科研技能来源。

## 构建与验证

环境：Python 3.10或以上、PyMuPDF、Matplotlib、XeLaTeX；当前使用TeX Live 2025。
Matplotlib重绘采用Times New Roman与宋体，其他系统需选择可用的对应字体。

```powershell
python -m pip install -r frontiers-review/requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File frontiers-review/build.ps1
```

构建先按引用顺序生成书目，再生成矢量图组，编译准备材料两遍、综述三遍，
核对字数、引用、姓名学号、PDF元信息、来源哈希、许可面板的矢量内容和页面边界。
上游AAS组合ccaption与caption产生一条“未知类，使用标准默认值”的已知提示，
构建仅豁免这一条，课程适配另设图注样式并做渲染检查；溢出、缺字、未定义引用和其他字体或包警告仍阻止交付。

`review-verification.json`记录技术检查，不虚构作者已核阅；
`review-visual-audit.json`记录最终渲染检查。
`report.tex`、`materials.tex`是早期样稿和阅读指南，不是当前完整综述。

## 课程要求

作业主题需与课内内容相关、便于同学互评；不少于3000字，包含问题引入、方法总结与本人理解，
图文并茂，提交按“姓名+学号.pdf”命名的PDF。
截止为2026-11-20 23:59，互评截止2026-12-05。
`inputs/`保存原资料副本，其中课堂概括属于二手材料，不作为论文结果的原始证据。
