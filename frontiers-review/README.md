# 工程技术前沿：多智能体文献综述

独立分支：`assignment-engineering-frontiers-review`，从仓库 `main` 建立。
没有继承MP2分支的代码、实验、个人课程信息或小组贡献声明。

## 完整综述初稿

按后续要求新增 `review.tex`，正文已写完，不再只有提纲。题目为
“面向科研任务的多智能体系统：知识增强、记忆机制与可信性评估”，
含中文摘要、问题引入、知识增强、记忆、协作、可信性评价、讨论与结论。
有3幅原创矢量示意图、2张方法和评价比较表；另补充多智能体失败和内在自我纠错两篇原始论文，
共10篇编号引文。正文汉字保守计数排除摘要、标题、图、表和参考文献后超过3000。

完整初稿：`output/pdf/multi-agent-literature-review.pdf`，同步至课程目录的
`review/multi-agent-literature-review.pdf`；与原来的排版样稿、阅读材料分开保存。
本稿为AI辅助生成和整理，没有声称是作者已独立完成的作业，也没有编造个人经历或系统实验。
课程截图限制直接提交AI生成内容的规则仍有效，需要作者核阅、修改并确认允许的使用范围。
姓名和学号未知，封面保留待填字段，尚未按个人正式文件名打包或上传。
`review-verification.json` 记录正文字数、图表、引用、PDF哈希和待完成项。

## 已完成的工作

已阅读作业文字说明、课件截图，以及课内概括Markdown链接的长图。拟定主题为
“面向科研任务的多智能体系统：知识增强、记忆机制与可信性评估”。
范围围绕课内的知识增强、长上下文、记忆和科研验证，避免扩展成过于宽泛的AI技术盘点。
基础阅读材料选取八篇论文，完整综述补充至十篇，均为目的性选择的原始文献，非穷尽式或系统综述。

MP2模板不宜直接提交：其实验章节、课程号、教学班、组员和英文提交设置不适用。
本项目复用官方ZJUI矢量标识和封面字号原则，重写为中文个人综述版式，
12pt正文、编号参考文献、方法比较表及原创概念关系图。
封面原则参考 `assignment2-advanced-ai@9a46ef1`；没有复用其学术正文。
官方标识来源：[ZJUI视觉规范](https://zjui.intl.zju.edu.cn/sites/default/files/2023-02/ZJUI%20VI.pdf)，
第1页横向彩色组合，原PDF裁取范围 `(128,90,454,149)`，保持颜色、字形和比例。
该标识权利归相应机构；本项目是个人课程排版，并非学校官方指定模板。

## 课程约束与当前状态

作业要求与课内内容相关、不少于3000字、图文并茂，包含问题引入、方法总结与本人理解，
PDF文件按“姓名+学号.pdf”命名。截止时间2026年11月20日23:59，互评截止12月5日。
课件截图还明确禁止直接提交AI生成内容。目前已按后续指令写完中文综述初稿，
并验证正文字数、图表和引文，但这不等于作者已独立完成并符合AI使用规则。
作者姓名、学号和本人核阅仍待完成。没有把AI初稿冒充为作者独立完成的作业，
也没有建立正式submission目录或上传教学平台。

如继续完善初稿，请修改 `review.tex` 并在 `metadata.tex` 填入真实作者信息。
`report.tex` 保留为早期写作模板，不是当前完整正文。
仅有标题、引文或字数统计通过，不意味着满足课程对独立完成的要求。

## 文件

- `report.tex`：中文学术综述排版样稿，含章节任务、图表位置和八篇编号引文。
- `review.tex`、`review-references.tex`：完整综述正文及十篇编号参考文献。
- `review-sources.json`、`review-verification.json`：完整综述的十篇来源与独立检查记录。
- `materials.tex`：要求核对、模板判断、概念图、八篇阅读卡、比较维度与写作规划。
- `metadata.tex`：个人作者信息，当前明确标为待填写。
- `references.tex`：真实文献及固定arXiv版本。使用版本与首发年份分开标明。
- `sources.json`：公开论文链接、下载时间、页数和SHA256；全文PDF只作本地阅读缓存，不提交到Git。
- `inputs/`：用户给定作业资料及课堂概括长图的只读副本。课堂概括是二手材料，不能代替论文证据。
- `output/pdf/`：完整综述初稿与两份准备PDF；构建后同步到课程目录下的 `review/`。
- `verification.json`：来源、PDF与未完成项检查，不宣称已完成课程作业。

全文核查范围是摘要、相关方法、评估与局限部分的针对性阅读，没有声称精读全部论文的所有附录。
不报告本项目未运行的实验，不用跨论文不可比数值作排名。

## 构建与复核

需要Python（PyMuPDF）、XeLaTeX及中文字体。仓库根目录运行：

```powershell
python -m pip install -r frontiers-review/requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File frontiers-review/build.ps1
```

每个文件编译两遍，检查溢出、缺字和引用警告。`verify.py` 核对八篇来源、PDF中的
非提交稿标签、作者待填提示、页面边界和哈希。统计的全部中文字符包括提示，
不能作为最终3000字正文的通过证明。`verify_review.py` 则单独验证完整初稿：
正文计数排除摘要、标题、图、表及参考文献，检查3图、2表、十篇引文与页面边界。
该检查仍不确认作者身份或课程的独立完成要求。图片复核可用：

```powershell
pdftoppm -scale-to 1400 -png frontiers-review/output/pdf/literature-review-layout.pdf frontiers-review/tmp/pdfs/layout
pdftoppm -scale-to 1400 -png frontiers-review/output/pdf/reading-and-writing-guide.pdf frontiers-review/tmp/pdfs/guide
pdftoppm -scale-to 1400 -png frontiers-review/output/pdf/multi-agent-literature-review.pdf frontiers-review/tmp/pdfs/review
```

源文件和文献链接可以继续使用；完成本人正文后仍需人工检查论点、引文、图表及格式。
