# 工程技术前沿：多智能体科研综述

分支 `assignment-engineering-frontiers-review` 从 `main` 建立。
个人课程作业，作者蒋佳豪，学号22671064；不继承MP2的课程号、小组信息、代码或实验。

## 当前稿件

题目：**面向科研任务的多智能体系统综述：知识、记忆与协作的机制及证据边界**。

正文围绕知识、状态和控制建立分类，再比较计算研究、假设生成和实体实验，
讨论失败机制、公平对照、证据核验及本文理解。
含中文及英文摘要、4幅图、3张表，15项研究与1项单独标注的写作工具来源。
保守正文汉字数排除摘要、标题、图表、公式及参考文献后超过8700，满足不少于3000字的长度要求。
没有虚构新实验、论文录用、人工核阅或跨系统胜率排名。

稳定预览：`output/pdf/multi-agent-literature-review.pdf`。
个人命名文件：`output/pdf/蒋佳豪22671064.pdf`。
构建后同步到课程目录 `review/`，并将个人命名PDF单独复制到课程目录 `submission/`。
阅读指南与排版样稿保留在 `review/`，不混入 `submission/`。

这是使用AI辅助整理、写作和绘图的课程修订稿；稿末保留资料与工具说明。
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

- `review-sources.json`：15项研究的全文链接、版本、页数及SHA256。
- `evidence-extraction.csv`：提取定位、在综述中的用途及边界。
- `research-notes.md`：叙述综述范围、本轮实际查询和防误读记录。
- `data/`：从原文表格逐项提取的数字，未将不同论文的分数合并排名。
- `make_figures.py`、`figure-provenance.json`：数值图重绘及转换记录。
- `figure-*.tex`：两幅概念矢量图，与两幅数值图的性质分别说明。

两个数值图分别来自ReAct表1和Luo等固定预印本v2表11；
原PDF对应页面已打开核对，图注说明模型、指标、样本、预算差异和缺陷注入。
未添加无法由原文支持的误差条。完整PDF只在忽略的 `cache/` 本地阅读，不打包提交、不上传Git。

已安装并参考K-Dense的 `literature-review` 和 `scientific-visualization`。
工具论文单独列为第16项，不计入15项研究；它们不是Nature官方技能。
详见 `research-notes.md` 的科研技能来源。

## 构建与验证

环境：Python 3.10或以上、PyMuPDF、Matplotlib、XeLaTeX；当前使用TeX Live 2025。
Matplotlib重绘默认使用Windows的Microsoft YaHei字体，其他系统需选择可用的中文字体。

```powershell
python -m pip install -r frontiers-review/requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File frontiers-review/build.ps1
```

构建生成数值图，编译准备材料两遍、综述三遍，并核对字数、引用、姓名学号、PDF元信息、来源哈希和页面边界。
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
