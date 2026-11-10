# 文献范围、写作修订与图表依据

资料核对日期：2026-11-09；编辑修订：2026-11-10。综述类型：叙述性综述。
未宣称穷尽检索、双人筛选、PRISMA系统综述或元分析。

## 范围与版本

32篇学术报告，含3篇相关综述和不同版本的研究报告；写作工具来源另存仓库记录。
The AI Scientist的2024预印本、2025第二版与2026期刊报告在来源清单中关联，
不作为三次独立复现。其余固定版本与全文校验值见 `review-sources.json`。
在获取的原始PDF中针对性阅读了方法、评价及局限，未宣称逐页精读所有长附录。

资料发现使用学术域名限制的网络查询、论文题名检索与引用追踪。
11月9日资料扩展时的实际查询包括（11月10日修订沿用本地全文，未新增网络检索）：

- `site.arxiv.org survey LLM agents scientific discovery multi agent science review 2025 taxonomy`
- `site.aas.net.cn 大语言模型 智能体 综述 科学 发现`
- `site.jos.org.cn 大语言模型 多智能体 综述`
- `site.nature.com "Towards an AI co-scientist" 2026`
- `site.arxiv.org "Language agents achieve superhuman synthesis"`
- `site.arxiv.org "AI Scientist-v2"`
- `site.arxiv.org "ResearchAgent" "2024"`
- `site.nature.com "Augmenting large language models with chemistry tools"`
- `site.aclanthology.org "ResearchAgent: Iterative"`
- `site.nature.com "The AI Scientist" "2026" "651"`

检索命中不作为事实验证；结果用于定位arXiv、ACL Anthology及期刊原文。
未使用新闻、商业摘要网站或其他综述的参考文献列表来代替原始结果核对。

## 真实综述的参考方式

已打开并参考以下综述的章节、表达与图表组织：

1. 郑逸宁等，《大语言模型的工具使用综述》，自动化学报2025，
   <https://doi.org/10.16383/j.aas.c240793>。
   参考其从定义、发展路径到机制和应用的连续论述；已查看PDF排版页。
2. Zheng等，From Automation to Autonomy，EMNLP 2025，
   <https://aclanthology.org/2025.emnlp-main.895/>。
   比较其自主层次与本文功能分层的不同。
3. Wei等，From AI for Science to Agentic Science，固定v2，
   <https://arxiv.org/abs/2508.14111v2>。
   对照能力、研究过程与领域应用的关系，未照搬其整体分类或插图。
4. 陈旭，《基于大语言模型的自主智能体概述》，CCL 2024前沿综述，
   <https://aclanthology.org/2024.ccl-2.8.pdf>。
   用于中文学术表达与功能分析的编辑参照，未据此转述实验数据。

本稿由课内知识增强、记忆和自动科研问题出发形成独立论述，
没有拼接上述综述的段落，也不将别人的分类直接写成本文原创贡献。
“问题引入、方法总结、自己的理解”分别落实到引言、方法比较和综合讨论。

## 图表数据和许可

11月10日删去总框架、抽象协作拓扑和研究闭环三图，避免用通用框箭图重复正文。
图1为按真实年份等距排布的代表文献分布；ChemCrow按2024年期刊版定位，其余基础工作按首次报告年份。
图2比较片段、摘要树及社区图索引，明确节点与查询选择的含义，不混入原方法没有采用的记忆状态字段。
图3提取Coscientist原图1abc，包含实际架构、模块任务及实验装置照片；提取范围为PDF第2页`(39,48,565,383)`。
图4为Coscientist原图5i、5j的未经曲线处理的矢量面板，不再并列一个通用流程图。
来源：Boiko等，Nature 2023，<https://doi.org/10.1038/s41586-023-06792-0>；
原文PDF许可段注明CC BY 4.0。提取页为PDF第6页，面板范围分别为
`(395,376,477,528)`与`(478,376,561,528)`；保留坐标、刻度、单位、曲线及数值，仅调整排列。
已检查m/z标签与最右刻度完整。

图5由ScienceAgentBench固定v3表3（PDF第8页）重绘，
选取GPT-4o和Claude 3.5 Sonnet在无专家知识下的全部三种框架。
两模型的执行率、任务成功率与费用保存于 `data/scienceagentbench.csv`。
基准有102项任务，每项独立运行三次后，按SR、VER、CodeBERTScore、较低费用依次择优，
再汇总入选运行的指标；不是三次运行均值。费用和模型版本均属原论文时期。
不把执行率解释为科学发现成功率，也不把历史API费用当成现行价格。

图6由Luo等固定v2第6.2节及表11（PDF第16—18页）重绘。
100个审计案例，每类20例，正负均衡，部分缺陷由原作者受控注入。
数据保存于 `data/audit.csv`，图中用原准确率乘以每类20例，精确换算为识别正确的案例数，不用于估计自然缺陷发生率。
数值图都只展示原表点估计，没有补造误差条或显著性。

## 来源与写作技能

已安装并读取K-Dense的 `literature-review`、`scientific-writing` 和 `scientific-visualization`：
<https://github.com/K-Dense-AI/scientific-agent-skills>。
工具出处原列第33项，作者、题名及年份已对照arXiv记录；按作者要求删除文末工具说明后，迁移到 `tool-provenance.json`，不作为正文参考文献。
技能不是Nature官方模板，也不是科学质量认证。

引用按首次出现排序，正文多篇引用排序并压缩；期刊、会议和电子报告标注类型。
原始版本链接保留，文中数据优先对应固定全文，避免混合版本。
`evidence-extraction.csv`记录来源的主要用途和定位，来源清单为每篇分配E编号。
AI助手已访问原文并进行提取及一致性检查；作者人工核验状态未被虚构为完成。
按作者要求，PDF删除“资料与工具说明”段落，页脚改为“工程技术前沿课程论文”。
AI辅助、工具出处与作者核阅状态仍如实记录于仓库；未向教学平台或期刊投稿。
