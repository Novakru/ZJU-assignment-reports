# ZJU 技术报告 / 论文模板

这是一个独立的英文 LaTeX 模板，用于浙江大学主题的技术报告、预印本和会议论文。模板使用求是蓝（`RGB 0,63,136`），正文与标题采用衬线字体，摘要使用带圆角的蓝色边框。

本模板为个人维护的非官方模板，不代表浙江大学官方格式。示例标题、作者、摘要和正文内容均为占位内容。

## 编译

使用 XeLaTeX 编译。Overleaf 请将编译器设为 XeLaTeX；本地可以运行：

```sh
latexmk -xelatex zju-tech-report.tex
```

模板使用 TeX Gyre Termes 作为衬线字体，Latin Modern Sans 和 Latin Modern Mono 作为无衬线及等宽字体。

## 模式切换

在 `zju-tech-report.tex` 开头设置：

```latex
\newcommand{\ReportMode}{report} % report 或 paper
```

### 技术报告模式

技术报告模式默认使用：

```latex
\newcommand{\ReportAuthorPlacement}{back}
```

此时首页标题下显示 `ReLER Lab, Zhejiang University`，作者列表放在参考文献之后。实验室 Logo 与浙大 Logo 并排放在首页顶栏。

如果希望作者和实验室都出现在首页，可以改为：

```latex
\newcommand{\ReportAuthorPlacement}{front}
```

此时标题下依次显示作者、`ReLER Lab, Zhejiang University` 和作者说明，作者列表不会在文末重复出现。

### 论文模式

设置：

```latex
\newcommand{\ReportMode}{paper}
```

论文模式会在首页标题下显示作者、单位和实验室 Logo。作者姓名使用衬线字体。

## 页眉与页码

模板采用双面排版，页码统一放在页脚中央。

论文模式默认使用：

- 奇数页左上角：短标题
- 偶数页右上角：短作者

技术报告模式默认在续页右上角显示短标题。四个页眉位置可以独立修改，也可以留空：

```latex
\renewcommand{\ReportOddLeftHeader}{\ReportShortTitle}
\renewcommand{\ReportOddRightHeader}{}
\renewcommand{\ReportEvenLeftHeader}{}
\renewcommand{\ReportEvenRightHeader}{\ReportShortAuthors}
```

模板使用 `twoside`，因此奇偶页的页眉位置会分别生效。

## 可修改字段

模板开头集中定义了常用信息：

- `\ReportTitle`：完整标题
- `\ReportShortTitle`：页眉短标题
- `\ReportShortAuthors`：页眉短作者
- `\ReportAuthors`：完整作者列表
- `\ReportLabName`：实验室名称
- `\ReportInstitution`：技术报告模式显示的机构名称
- `\ReportAffiliations`：作者单位
- `\ReportAuthorNotes`：作者脚注
- `\ReportNumber`、`\ReportDate`：报告编号和日期
- `\ReportContact`、`\ReportKeywords`：通信信息和关键词
- `\ZJULogo`、`\LabLogo`：浙大 Logo 和实验室 Logo 路径

`assets/` 中已经放入当前使用的浙大横向 Logo 和实验室 Logo，可以替换为其他已获授权的版本。

## 适用范围

会议投稿应优先使用会议官方模板；本模板适合技术报告、预印本、实验室内部报告和项目总结等场景。中文报告可以沿用版式结构，再改用 CTeX 文档类和中文字体设置。
