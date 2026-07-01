# T0 Assistant V1

第一版目标：在 Mac 上一键抓取当天市场和三只股票数据，自动给出四家T0量化分配建议，并写入 Excel。

## 1. 安装准备

建议用 VS Code 或 Cursor。Mac 自带终端也可以。

打开终端，进入项目目录：

```bash
cd ~/Downloads/t0_assistant_v1
```

创建虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

如果国内网络安装慢，可用：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 2. 运行

```bash
python main.py
```

运行后会生成：

- `data/T0_每日记录.xlsx`：每日数据和建议金额
- `reports/report_YYYY-MM-DD.html`：当天建议报告
- `data/market_YYYY-MM-DD.json`：原始行情数据

## 3. 你每天需要做什么

盘前或盘中运行一次：

```bash
python main.py
```

查看报告里的建议。

收盘后打开：

```text
data/T0_每日记录.xlsx
```

填写四家量化实际收益：

- 非凸实际收益
- 卡方实际收益
- 皓兴实际收益
- 跃然实际收益
- 备注：是否卖飞、是否异常、主观评价

## 4. 修改持仓

打开 `config.py`，修改：

```python
INITIAL_POSITIONS = {
    "景旺电子": 58256,
    "中际旭创": 387129,
    "胜宏科技": 387156,
}
```

后续版本会加截图 OCR 自动识别持仓。

## 5. 注意

这是决策辅助工具，不是自动交易工具。第一版规则很简单，重点是把数据流跑通。连续记录 2~4 周后，规则会用你的真实收益数据迭代。
