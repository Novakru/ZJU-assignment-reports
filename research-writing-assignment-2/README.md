# 科学研究与写作指导 作业二

[report.tex](report.tex) 是提交版的 LaTeX 源文件，沿用本仓库的 [ZJU 技术报告模板](../zju-tech-report/zju-tech-report.tex) 和 [ZJUI 矢量标识](../zju-tech-report/assets/zjui-horizontal-color.pdf)。

提交时将[五页报告 PDF](<科学研究写作 作业2 完成版.pdf>)与[原论文全文](ELLMER_Nature_Machine_Intelligence_2025.pdf)一同附上。[原始题目备份](<科学研究写作 作业2 原始备份.docx>)保留课程提供的作业说明。

## 编译

在本目录运行以下命令。需要安装 XeLaTeX、CTeX 与 PGFPlots 宏包、宋体（SimSun）和黑体（SimHei）。

```sh
latexmk -xelatex report.tex
```
