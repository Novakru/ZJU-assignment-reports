# 工程技术前沿：多智能体文献综述准备

独立分支：`assignment-engineering-frontiers-review`，从仓库 `main` 建立。
没有继承MP2分支的代码、实验、个人课程信息或小组贡献声明。

## 已完成的工作

已阅读作业文字说明、课件截图，以及课内概括Markdown链接的长图。拟定主题为
“面向科研任务的多智能体系统：知识增强、记忆机制与可信性评估”。
范围围绕课内的知识增强、长上下文、记忆和科研验证，避免扩展成过于宽泛的AI技术盘点。
文献是目的性选择的八篇代表性原始论文，非穷尽式或系统综述。

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
课件截图还明确禁止直接提交AI生成内容。因此本分支当前交付的是学习辅助与排版样稿，
不是可以直接提交的完整综述。作者姓名、学号、本人原创正文及最终字数核验仍待完成。
没有把AI阅读卡冒充为作者独立完成的3000字作业，也没有建立正式submission目录。

请将自己的阅读笔记、观点和例子补入 `report.tex`，移除写作提示，再整理为最终正文。
仅有标题、引文或字数统计通过，不意味着满足课程对独立完成的要求。

## 文件

- `report.tex`：中文学术综述排版样稿，含章节任务、图表位置和八篇编号引文。
- `materials.tex`：要求核对、模板判断、概念图、八篇阅读卡、比较维度与写作规划。
- `metadata.tex`：个人作者信息，当前明确标为待填写。
- `references.tex`：真实文献及固定arXiv版本。使用版本与首发年份分开标明。
- `sources.json`：公开论文链接、下载时间、页数和SHA256；全文PDF只作本地阅读缓存，不提交到Git。
- `inputs/`：用户给定作业资料及课堂概括长图的只读副本。课堂概括是二手材料，不能代替论文证据。
- `output/pdf/`：两份准备PDF；构建后同步到课程目录下的 `review/`。
- `verification.json`：来源、PDF与未完成项检查，不宣称已完成课程作业。

全文核查范围是摘要、相关方法、评估与局限部分的针对性阅读，没有声称精读八篇论文的全部附录。
不报告本项目未运行的实验，不用跨论文不可比数值作排名。

## 构建与复核

需要Python（PyMuPDF）、XeLaTeX及中文字体。仓库根目录运行：

```powershell
python -m pip install -r frontiers-review/requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File frontiers-review/build.ps1
```

每个文件编译两遍，检查溢出、缺字和引用警告。`verify.py` 核对八篇来源、PDF中的
非提交稿标签、作者待填提示、页面边界和哈希。统计的全部中文字符包括提示，
不能作为最终3000字正文的通过证明。图片复核可用：

```powershell
pdftoppm -scale-to 1400 -png frontiers-review/output/pdf/literature-review-layout.pdf frontiers-review/tmp/pdfs/layout
pdftoppm -scale-to 1400 -png frontiers-review/output/pdf/reading-and-writing-guide.pdf frontiers-review/tmp/pdfs/guide
```

源文件和文献链接可以继续使用；完成本人正文后仍需人工检查论点、引文、图表及格式。
