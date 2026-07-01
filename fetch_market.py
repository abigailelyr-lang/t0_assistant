# -*- coding: utf-8 -*-

from __future__ import annotations

from datetime import datetime
import akshare as ak


def _safe_float(value):
    try:
        if value in [None, "", "--"]:
            return None
        return float(value)
    except Exception:
        return None


def fetch_indices():
    """
    抓取主要指数数据。
    使用东方财富指数实时行情接口。
    """
    result = {}
    errors = []

    index_map = {
        "上证指数": "000001",
        "创业板指": "399006",
        "深证成指": "399001",
    }

    try:
        df = ak.stock_zh_index_spot_em()
        for name, code in index_map.items():
            row = df[df["代码"].astype(str) == code]
            if row.empty:
                result[name] = {"最新价": None, "涨跌幅": None}
                errors.append(f"没有找到指数：{name} {code}")
                continue

            r = row.iloc[0]
            result[name] = {
                "最新价": _safe_float(r.get("最新价")),
                "涨跌幅": _safe_float(r.get("涨跌幅")),
            }

    except Exception as e:
        errors.append(f"指数数据抓取失败：{e}")
        for name in index_map:
            result[name] = {"最新价": None, "涨跌幅": None}

    return result, errors


def fetch_stocks(stocks: dict):
    """
    抓取个股实时行情。
    stocks 来自 config.py，例如：
    {
        "景旺电子": "603228",
        "中际旭创": "300308",
        "胜宏科技": "300476"
    }
    """
    result = {}
    errors = []

    try:
        df = ak.stock_zh_a_spot_em()

        for name, code in stocks.items():
            row = df[df["代码"].astype(str) == str(code)]
            if row.empty:
                result[name] = {
                    "代码": code,
                    "最新价": None,
                    "涨跌幅": None,
                    "振幅": None,
                    "换手率": None,
                    "成交额": None,
                }
                errors.append(f"没有找到股票：{name} {code}")
                continue

            r = row.iloc[0]
            result[name] = {
                "代码": code,
                "最新价": _safe_float(r.get("最新价")),
                "涨跌幅": _safe_float(r.get("涨跌幅")),
                "振幅": _safe_float(r.get("振幅")),
                "换手率": _safe_float(r.get("换手率")),
                "成交额": _safe_float(r.get("成交额")),
            }

    except Exception as e:
        errors.append(f"个股数据抓取失败：{e}")

        for name, code in stocks.items():
            result[name] = {
                "代码": code,
                "最新价": None,
                "涨跌幅": None,
                "振幅": None,
                "换手率": None,
                "成交额": None,
            }

    return result, errors


def fetch_with_akshare(stocks: dict):
    """
    主函数：main.py 会调用这个函数。
    返回一个统一的数据字典。
    """
    today = datetime.now().strftime("%Y-%m-%d")

    indices, index_errors = fetch_indices()
    stock_data, stock_errors = fetch_stocks(stocks)

    return {
        "date": today,
        "data_source": "akshare",
        "indices": indices,
        "stocks": stock_data,
        "errors": index_errors + stock_errors,
    }