# -*- coding:utf-8 -*-
"""
V3.0 数据抓取引擎 (双色球专属极简版)
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
import os

from config import name_path, data_file_name
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_url():
    """获取 500彩票网 的数据接口"""
    # 直接硬编码双色球 ssq 路径
    url = "https://datachart.500.com/ssq/history/"
    path = "newinc/history.php?start={}&end="
    return url, path


def get_current_number():
    """获取最新一期期号"""
    url, _ = get_url()
    r = requests.get(f"{url}history.shtml", verify=False)
    r.encoding = "gb2312"
    soup = BeautifulSoup(r.text, "lxml")
    current_num = soup.find("div", class_="wrap_datachart").find("input", id="end")["value"]
    return current_num


def spider(start, end):
    """核心爬虫逻辑"""
    url, path = get_url()
    url = f"{url}{path.format(start)}{end}"
    r = requests.get(url=url, verify=False)
    r.encoding = "gb2312"
    soup = BeautifulSoup(r.text, "lxml")
    trs = soup.find("tbody", attrs={"id": "tdata"}).find_all("tr")

    data = []
    for tr in trs:
        item = dict()
        item["期数"] = tr.find_all("td")[0].get_text().strip()
        for i in range(6):
            item[f"红球_{i + 1}"] = tr.find_all("td")[i + 1].get_text().strip()
        item["蓝球"] = tr.find_all("td")[7].get_text().strip()
        data.append(item)

    df = pd.DataFrame(data)
    # 直接存入 config 中配置的根目录
    save_path = os.path.join(name_path["ssq"]["path"], data_file_name)
    df.to_csv(save_path, encoding="utf-8", index=False)
    return df


def run():
    current_number = get_current_number()
    play_name = name_path["ssq"]["name"]
    logger.info(f"【{play_name}】最新开奖期号：{current_number}")
    logger.info(f"📡 正在全网拉取【{play_name}】历史数据...")

    data = spider(1, current_number)

    # 验证扁平化目录下的 data.csv 是否生成成功
    if data_file_name in os.listdir(name_path["ssq"]["path"] or "."):
        logger.info(f"✅ 【{play_name}】数据同步完毕！共拦截 {len(data)} 期历史情报。")
    else:
        logger.error("❌ 数据写入失败，请检查目录权限！")


if __name__ == "__main__":
    run()