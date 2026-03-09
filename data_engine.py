import pandas as pd
import numpy as np
import os
from collections import Counter


def load_data():
    """基础功能：安全加载历史数据"""
    data_path = 'data.csv'
    if not os.path.exists(data_path):
        print("❌ 找不到数据文件！请确保已经运行了抓取数据的脚本。")
        return None
    return pd.read_csv(data_path)


# =====================================================================
# 🧠 核心模块一：蓝球 V3.0 机器学习多维特征库 (供 AI 训练使用)
# =====================================================================
def build_advanced_blue_windows(total_lookback=1000, window_size=25):
    """提取奇偶、大小、跨度等多维特征，并将标签升级为 1-16 分类"""
    df = load_data()
    if df is None: return [], []

    df = df.tail(total_lookback).reset_index(drop=True)
    blues = df.iloc[:, -1].values.astype(int)

    X_windows = []
    Y_targets = []

    for i in range(len(df) - window_size):
        window = blues[i: i + window_size]
        target = blues[i + window_size]  # 真实的下一期蓝球号码

        counts = Counter(window)
        never_appeared = 16 - len(counts)  # 特征1：冷号积压度
        max_freq = max(counts.values()) if counts else 0  # 特征2：热号最高频次
        odds_count = sum(1 for x in window if x % 2 != 0)  # 特征3：奇偶偏态 (奇数个数)
        bigs_count = sum(1 for x in window if x >= 9)  # 特征4：大小比重心 (大号个数)

        # 特征5：平均跨度 (近期震荡幅度)
        spans = [abs(window[j] - window[j - 1]) for j in range(1, len(window))]
        avg_span = sum(spans) / len(spans) if spans else 0

        # 组装超级特征矩阵 X，并将真实的号码作为 Y
        X_windows.append([never_appeared, max_freq, odds_count, bigs_count, avg_span])
        Y_targets.append(target)

    return np.array(X_windows), np.array(Y_targets)


# =====================================================================
# 📈 核心模块二：蓝球马尔可夫转移矩阵 (物理掉落概率推演)
# =====================================================================
def get_blue_markov_matrix():
    """计算历史中出完 A 号码后，紧接着出 B 号码的概率分布"""
    df = load_data()
    blues = df.iloc[:, -1].values.astype(int)

    # 初始化 17x17 矩阵 (为了方便用 1-16 的真实号码做索引，舍弃 0 索引)
    matrix = np.zeros((17, 17))
    for i in range(len(blues) - 1):
        curr_ball = blues[i]
        next_ball = blues[i + 1]
        matrix[curr_ball][next_ball] += 1
    return matrix


# =====================================================================
# 🔥 核心模块三：红球 EMA 指数移动平均 (金融级动量追踪)
# =====================================================================
def get_red_ema_momentum(lookback=50):
    """用金融算法计算每个红球的当下热度（越近出现的权重呈指数级拉高）"""
    df = load_data()
    reds_history = df.tail(lookback).iloc[:, -7:-1].values

    ema_scores = {i: 0.0 for i in range(1, 34)}
    alpha = 2.0 / (lookback + 1)  # EMA 平滑常数

    for row in reds_history:
        for num in range(1, 34):
            if num in row:
                # 如果近期出现了，动量拉升
                ema_scores[num] = (1 * alpha) + (ema_scores[num] * (1 - alpha))
            else:
                # 如果没出现，动量衰减
                ema_scores[num] = (0 * alpha) + (ema_scores[num] * (1 - alpha))

    return ema_scores


# =====================================================================
# 🤝 核心模块四：红球 Apriori 关联矩阵 (数据挖掘黄金搭档)
# =====================================================================
def get_red_co_occurrence_matrix():
    """找出全量历史中，哪些红球最喜欢抱团一起出"""
    df = load_data()
    reds_history = df.iloc[:, -7:-1].values.astype(int)

    matrix = np.zeros((34, 34))
    for row in reds_history:
        for i in range(len(row)):
            for j in range(i + 1, len(row)):
                matrix[row[i]][row[j]] += 1
                matrix[row[j]][row[i]] += 1  # 互相增加绑定值
    return matrix


# 测试驱动：你可以直接运行这个文件看看引擎爆发的威力！
if __name__ == '__main__':
    print("================ ⚙️ V3.0 量化数据引擎自检 ================")

    print("\n[1] 正在测试 AI 多维特征提取...")
    X, Y = build_advanced_blue_windows(total_lookback=200, window_size=25)
    print(f"✅ 成功生成 {len(X)} 组多维特征集。例：近期奇数={X[-1][2]}个, 平均跨度={X[-1][4]:.1f}")

    print("\n[2] 正在测试蓝球马尔可夫转移矩阵...")
    markov = get_blue_markov_matrix()
    test_ball = 5
    most_likely_next = np.argmax(markov[test_ball][1:]) + 1
    print(f"✅ 矩阵推演：历史上开出 [{test_ball:02d}] 之后，最爱接的号码是 [{most_likely_next:02d}]")

    print("\n[3] 正在测试红球 EMA 动量追踪...")
    ema = get_red_ema_momentum(lookback=50)
    top_hot = sorted(ema.items(), key=lambda x: x[1], reverse=True)[0][0]
    print(f"✅ 动量锁定：当下 EMA 动量最强的红球是 [{top_hot:02d}]")

    print("\n[4] 正在测试红球 Apriori 关联矩阵...")
    co_matrix = get_red_co_occurrence_matrix()
    test_red = 12
    best_partner = np.argmax(co_matrix[test_red][1:]) + 1
    print(f"✅ 数据挖掘：红球 [{test_red:02d}] 的历史终极黄金搭档是 [{best_partner:02d}]")

    print("\n🚀 引擎各项指标运转完美！随时可以对接 AI 中枢！")
    print("=====================================================")