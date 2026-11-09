# 综述范围与证据记录

核对日期：2026-11-09。类型：问题导向叙述性综述。

目标是解释知识组织、持久状态和代理协作怎样影响科研结论的可核验性。
15项研究采用目的性选择，覆盖基础机制、科研系统及负面证据；不是PRISMA系统综述，
没有声称检索穷尽、双人筛选、数据库结果总数或进行了新实验。

## 本轮补充检索

以下是实际使用的发现性网络查询。它们是补充检索，不能代替完整数据库检索。

- `Towards an AI co-scientist 2025 arxiv 2502.18864 scientific validation`
- `site.nature.com "Virtual Lab" "nanobodies" 2025 Swanson`
- `site.nature.com "Autonomous chemical research" Boiko MacKnight 2023`
- `site.arxiv.org "The Virtual Lab" Swanson 2024`
- `"The more you automate, the less you see" authors 2026`
- `"The more you automate" "arxiv"`

通过arXiv元数据、Nature原文和原文参考文献链补充五项研究；后续从原始站点获取完整PDF，
在本地读取相关机制、评价和局限。没有使用新闻或商业论文摘要作为正文证据。
GraphRAG等原有十项来源复用已下载的固定版本全文。

Virtual Lab和Coscientist采用Nature正式稿，避免与早期预印本混计。
Luo等的结果图固定引用2025-12-20的arXiv v2；检索还发现2026年的后续出版记录，
但没有将后续版本的数据、表号和样本设置混入本图。
AI co-scientist固定v1，MAST固定v2。版本选择是为保证可核对，不表示这些一定是最新版本。

## 提取与核对

`evidence-extraction.csv`记录研究、定位、本文用途与限制。
`review-sources.json`记录全文下载链接、页数和SHA256。
全文PDF及文字缓存仅用于本地阅读，不打入提交包，也不上传Git。

两组图表数值保存为 `data/react.csv` 与 `data/audit.csv`。
已打开原PDF对应页面逐项核对，图由 `make_figures.py` 重绘。
原表没有本图需要的重复运行区间，不补造误差条；不合并不同论文的性能分数。

关键防误读处理：

- ReAct不是多代理对照；CoT-SC有额外采样，图不能证明相同预算下的优势。
- Agent Laboratory的6.1与3.8属于原文特定自动/人工评分比较。
- Virtual Lab的92个候选、78个更高AF分数和60个更优Rosetta分数，不组成通用发现成功率。
- 审计研究每类20例，其中一部分阳性为注入缺陷，不据此估计自然缺陷发生率。
- 等相关方差公式是有明确假设的数学说明，不是测量得到的代理相关性或投票准确率。
- 图1、图2与评价设计为分析建议，未冒充原文已验证架构或本项目新实验。

## 科研技能与排版来源

已安装并参考K-Dense的 `literature-review` 与 `scientific-visualization`：

- <https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/literature-review>
- <https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/scientific-visualization>

工具来源文献（正文参考文献第16项，单独说明，不计入15项研究）：
Kassis T, Agarwal V, He Y, Patel D, Brueckner A M. Scientific Agent Skills: A Library of
Procedural Knowledge for Research Agents. 2026. <https://doi.org/10.48550/arXiv.2609.00065>。
作者、题名与年份已从arXiv记录核对；没有声称它是Nature官方工具。

排版采用《自动化学报》官网当前可下载的2026-09-09版 `aas.cls`。
已先编译原始模板，成功产生4页样稿；原类文件和picins保持原样。
适配放在 `journal-review.sty`：加入ZJUI官方矢量标识和个人课程信息，移除期刊发表元数据，
正文11pt、双栏、三线表及编号引文。来源、原始文件哈希与下载时间见 `template-source.json`。

本稿使用AI辅助资料整理、写作和绘图，未声称已获得作者人工核阅或课程提交许可。
技术检查与打包完成不等于作者已确认其科学判断及课程AI使用合规性。
