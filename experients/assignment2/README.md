# MP2 实验

- `run_experiments.py`：12组铺砌、4组指定对局、40组随机对局。
- `checks.py`：评估优先级、即时胜负、同分顺序、满目标棋盘、搜索等价性、输入不变性和逐步回放验证。
- `results.json`：实际运行结果，保存各回合棋盘、落子、分值与节点数；沿用模板迁移前的实验，未因排版修改而重跑并替换耗时。
- `tuning*.py`、`tune_*.py` 与对应 JSON：开发阶段参数比较。随机起点只有18种，因此开发与最终实验存在条件重叠。
- `instances.py`、`Pentomino.py`：课程原始实例及验证器，未修改。

随机协议：`random.Random(448)`，每局依次选择起始局部棋盘和先手。搜索深度固定为3；节点数包含根与叶节点。

当前12组铺砌通过、4组指定对局完成、自定义智能体40胜/40局。真人实验尚缺，不能用自动对局替代。

扩展实验：`run_extra.py`运行全局三连规则的12局对战，固定随机种子2013，结果为X胜5、O胜5、平局2。`extra_results.json`保存全程棋盘、落子、节点与局部归属。`check_extra.py`独立检查终盘归属、局部封闭、平局、全局三连、搜索等价性，并回放全部落子。

真人章节现为待录入版，自动日志位于 `human_games.json`（仅保存真正完成的局）。`human-notes.json`是观察文字的中英文空模板，不包含对局，也不会作为实验数据计数。

```powershell
python experients/assignment2/checks.py
python experients/assignment2/run_experiments.py
```

Part I只依赖标准库和NumPy；Part II只依赖标准库。ReportLab仅用于导出报告中的矢量棋盘。
