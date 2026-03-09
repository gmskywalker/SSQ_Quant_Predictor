# -*- coding:utf-8 -*-
"""
V3.0 系统基础配置
只保留数据抓取所需的必要字典，废弃所有原版深度学习参数
"""

# 定义红蓝球字段名称
ball_name = [
    ("红球", "red"),
    ("蓝球", "blue")
]

# 全局数据文件名
data_file_name = "data.csv"

# 玩法路径配置 (已扁平化，直接存根目录)
name_path = {
    "ssq": {
        "name": "双色球",
        "path": "./"
    }
}