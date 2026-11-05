# MP2 实验

- `run_experiments.py`：12组铺砌、4组指定对局、40组随机对局。
- `checks.py`：评估优先级、即时胜负、同分顺序、满目标棋盘、搜索等价性、输入不变性和逐步回放验证。
- `results.json`：实际运行结果，保存各回合棋盘、落子、分值与节点数；沿用模板迁移前的实验，未因排版修改而重跑并替换耗时。
- `tuning*.py`、`tune_*.py` 与对应 JSON：开发阶段参数比较。随机起点只有18种，因此开发与最终实验存在条件重叠。
- `instances.py`、`Pentomino.py`：课程原始实例及验证器，未修改。

随机协议：`random.Random(448)`，每局依次选择起始局部棋盘和先手。搜索深度固定为3；节点数包含根与叶节点。

当前12组铺砌通过、4组指定对局完成、自定义智能体40胜/40局。真人实验尚缺，不能用自动对局替代。

```powershell
python experients/assignment2/checks.py
python experients/assignment2/run_experiments.py
```

Part I只依赖标准库和NumPy；Part II只依赖标准库。ReportLab仅用于导出报告中的矢量棋盘。
