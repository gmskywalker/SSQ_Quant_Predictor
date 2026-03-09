import os
import sys
import time
import requests
import urllib3
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger

# 禁用烦人的 SSL 证书警告 (因为使用了 verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 500彩票网数据源
BASE_URL = "https://datachart.500.com/ssq/"


def safe_request(url):
    """
    🛡️ 核心防盾：带 VPN 冲突检测的网络请求包装器
    """
    try:
        # 强制清空 Python 运行时的代理环境变量 (防呆不防傻)
        os.environ["http_proxy"] = ""
        os.environ["https_proxy"] = ""

        # 发起请求
        r = requests.get(url, verify=False, timeout=15)
        r.raise_for_status()
        r.encoding = 'gbk'  # 500彩票网是 GBK 编码
        return r

    except Exception as e:
        error_msg = str(e)
        # 精准捕获 ProxyError 或底层的 FileNotFoundError (urllib3 代理 Bug)
        if "ProxyError" in error_msg or "FileNotFoundError" in error_msg or "Max retries exceeded" in error_msg:
            logger.error("\n" + "!" * 65)
            logger.error("🚨 [拦截警告] 发现网络代理冲突 (ProxyError)！")
            logger.error("👉 案发原因：系统检测到您当前开启了 VPN (梯子) 或系统代理。")
            logger.error("👉 目标阻断：500 彩票网是国内数据源，开启代理会导致底层握手崩溃。")
            logger.error("🛠️ 解决方法：请在电脑右下角【彻底退出 VPN / 代理软件】，然后重新运行！")
            logger.error("!" * 65 + "\n")
        else:
            logger.error(f"\n❌ 网络请求发生未知错误：\n{error_msg}\n请检查网络连接后重试。")

        # 抛出异常后优雅退出程序，不显示满屏红字报错
        sys.exit(1)


def get_current_number():
    """获取最近一期的开奖期号"""
    url = f"{BASE_URL}history/history.shtml"
    r = safe_request(url)

    soup = BeautifulSoup(r.text, 'lxml')
    tbody = soup.find('tbody', id='tdata')
    if not tbody:
        logger.error("❌ 无法解析网页，500彩票网可能更新了页面结构！")
        sys.exit(1)

    # 获取第一行数据（最新一期）
    latest_tr = tbody.find('tr')
    issue = latest_tr.find_all('td')[0].text.strip()
    return issue


def get_all_data():
    """拉取全网历史开奖数据"""
    logger.info("🕷️ 正在全网拉取最新开奖数据 (01_get_data.py)...")

    # 获取近 10000 期的接口（相当于全量拉取）
    url = f"{BASE_URL}history/newinc/history.php?start=00001&end=99999"
    r = safe_request(url)

    soup = BeautifulSoup(r.text, 'lxml')
    tbody = soup.find('tbody', id='tdata')

    if not tbody:
        logger.error("❌ 历史数据拉取失败！")
        sys.exit(1)

    trs = tbody.find_all('tr', class_=['t_tr1', 't_tr2'])

    data_list = []
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) < 8:
            continue

        # 提取期号、红球 1-6、蓝球
        issue = tds[0].text.strip()
        reds = [td.text.strip() for td in tds[1:7]]
        blue = tds[7].text.strip()

        row_data = [issue] + reds + [blue]
        data_list.append(row_data)

    # 组装为 DataFrame 格式
    columns = ['Issue', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'B1']
    df = pd.DataFrame(data_list, columns=columns)

    # 按照期号升序排列 (最老的在最上面，最新的在最下面)
    df = df.sort_values(by='Issue').reset_index(drop=True)

    # 保存到本地 CSV
    df.to_csv('data.csv', index=False, encoding='utf-8')
    logger.info(f"✅ 成功截获 {len(df)} 期历史开奖数据！已封存至 data.csv")
    return df


def run():
    """主控流水线"""
    # 尝试获取最新期号并测试网络
    current_number = get_current_number()
    logger.info(f"🎯 探针回传：当前最新期号为 [{current_number}]")

    # 开始全量拉取
    get_all_data()


if __name__ == "__main__":
    run()