# LaTeX 小组报告样例

`group-report.tex` 是一个课程项目报告起始样例，包含封面、章节结构、数学公式、表格、图片、代码块和算法环境的常用宏包配置。示例内容是占位内容，使用前请替换标题、组号、姓名和日期。

## 编译

使用 XeLaTeX 编译：

```sh
xelatex group-report.tex
```

该样例使用 `ctex`、`fontspec`、`listings`、`pgfplots`、`tcolorbox`、`tikz` 和 `algorithm2e` 等宏包。代码字体指定为 Consolas；如未安装该字体，可将 `\newfontfamily\menlo{Consolas}` 改成系统中可用的等宽字体。

这是个人整理的示例，不是学院或学校发布的正式格式。课程或学院有指定格式时，以官方要求为准。
