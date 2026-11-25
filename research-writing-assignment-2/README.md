# 科学研究与写作指导 作业二

- [完成版 PDF](<科学研究写作 作业2 完成版.pdf>) 使用仓库的 ZJUI 技术报告版式。提交时与[原论文全文](ELLMER_Nature_Machine_Intelligence_2025.pdf)一同附上。
- [可编辑 Word 版](<科学研究写作 作业2 完成版.docx>) 与 PDF 正文一致，使用 Word 原生标题、正文和表格。
- [原始题目备份](<科学研究写作 作业2 原始备份.docx>) 保留课程提供的作业说明。

## 重新编译 PDF

在本目录运行以下命令。需要 Pandoc、XeLaTeX、TeX Live 的 CTeX 宏包，以及宋体（SimSun）和黑体（SimHei）。

```sh
pandoc report.md --template=report-template.tex --pdf-engine=xelatex -o "科学研究写作 作业2 完成版.pdf"
```

[中文模板](report-template.tex) 源于仓库的 [ZJU 技术报告模板](../zju-tech-report/zju-tech-report.tex)，直接引用其中的 [ZJUI 矢量标识](../zju-tech-report/assets/zjui-horizontal-color.pdf)。正文在 [report.md](report.md) 中维护。
