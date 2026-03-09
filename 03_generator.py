import pandas as pd
import numpy as np
import random
import os
from collections import Counter
# 导入你强大的 V3.0 数据引擎组件
from data_engine import load_data, get_red_ema_momentum, get_red_co_occurrence_matrix, get_blue_markov_matrix


def generate_v3_numbers():
    print("============== ⚙️ 启动 V3.0 终极策略总装车间 ==============")
    df = load_data()
    if df is None: return

    # ---------------------------------------------------------
    # 📥 1. 获取所有 V3.0 的核心原材料
    # ---------------------------------------------------------
    recent_24 = df.tail(24).iloc[:, -7:-1].values.flatten().tolist()
    recent_100 = df.tail(100).iloc[:, -7:-1].values.flatten().tolist()
    last_draw_reds = df.tail(1).iloc[:, -7:-1].values.flatten().tolist()
    last_draw_blue = df.tail(1).iloc[:, -1].values[0]

    # 提取引擎数据
    ema_scores = get_red_ema_momentum(lookback=50)
    co_matrix = get_red_co_occurrence_matrix()
    blue_markov = get_blue_markov_matrix()

    # 获取 AI 蓝球指令
    try:
        with open('ai_blue_picks.txt', 'r') as f:
            ai_picks = f.read().strip().split(',')
            ai_top1, ai_top2 = int(ai_picks[0]), int(ai_picks[1])
        print(f"📥 成功接收 AI 钦点蓝球：状元[{ai_top1:02d}], 榜眼[{ai_top2:02d}]")
    except:
        print("⚠️ 未找到 AI 蓝球指令，启用随机备用方案。")
        ai_top1, ai_top2 = random.sample(range(1, 17), 2)

    red_matrix = []

    # ---------------------------------------------------------
    # 🔴 2. 红球 5 大阵型实体化
    # ---------------------------------------------------------
    print("正在锻造红球矩阵...")

    # 【注1: EMA 平滑追热】(从 EMA 前 15 名中，强制 3 个区间各选 2 个)
    top_15_ema = [x[0] for x in sorted(ema_scores.items(), key=lambda v: v[1], reverse=True)[:15]]
    z1 = [x for x in top_15_ema if 1 <= x <= 11] + random.sample(range(1, 12), 2)  # 加 random 是防止极端情况下池子太空
    z2 = [x for x in top_15_ema if 12 <= x <= 22] + random.sample(range(12, 23), 2)
    z3 = [x for x in top_15_ema if 23 <= x <= 33] + random.sample(range(23, 34), 2)
    r1 = random.sample(z1[:max(2, len(z1) - 2)], 2) + random.sample(z2[:max(2, len(z2) - 2)], 2) + random.sample(
        z3[:max(2, len(z3) - 2)], 2)
    red_matrix.append(sorted(r1))

    # 【注2: 破冰狙击】(2个极冷号 + 4个绝对温号)
    counts_100 = Counter(recent_100)
    avg_freq = sum(counts_100.values()) / len(counts_100)
    warm_pool = [k for k, v in counts_100.items() if abs(v - avg_freq) <= 1]  # 极其平庸的温号
    cold_pool = [x for x in range(1, 34) if x not in recent_24]  # 24期没出的冷号
    if len(cold_pool) < 2: cold_pool += [x[0] for x in counts_100.most_common()[-10:]]
    if len(warm_pool) < 4: warm_pool += [x[0] for x in counts_100.most_common()[10:25]]
    r2 = random.sample(cold_pool, 2) + random.sample(warm_pool, 4)
    red_matrix.append(sorted(r2))

    # 【注3: 关联矩阵】(找一个核心胆码，然后配它的黄金搭档)
    core_ball = random.choice(last_draw_reds)  # 拿上期的一个号做胆
    partners = np.argsort(co_matrix[core_ball])[::-1]  # 按关联度从高到低排序
    r3 = [core_ball]
    for p in partners:
        if p != 0 and p not in r3 and len(r3) < 6:
            r3.append(int(p))
    red_matrix.append(sorted(r3))

    # 【注4: 步长推演】(复用上期1-2个，其余用邻号填充)
    r4 = random.sample(last_draw_reds, random.choice([1, 2]))
    adj_pool = [x + 1 for x in last_draw_reds if x < 33] + [x - 1 for x in last_draw_reds if x > 1]
    adj_pool = list(set([x for x in adj_pool if x not in r4]))
    r4.extend(random.sample(adj_pool, min(len(adj_pool), 6 - len(r4))))
    while len(r4) < 6:  # 补齐
        new_ball = random.randint(1, 33)
        if new_ball not in r4: r4.append(new_ball)
    red_matrix.append(sorted(r4))

    # 【👑 注5: 宏观黄金防守】(极严苛死循环安检)
    freq_list = [x[0] for x in counts_100.most_common()]
    hot_p, warm_p, cold_p = freq_list[:11], freq_list[11:22], freq_list[22:]
    while True:
        r5 = random.sample(hot_p, 2) + random.sample(warm_p, 2) + random.sample(cold_p, 2)
        s_val = sum(r5)
        odd_cnt = sum(1 for x in r5 if x % 2 != 0)
        # 安检条件：和值 90-130 之间，奇数 2-4 个之间（即奇偶比2:4, 3:3, 4:2）
        if 90 <= s_val <= 130 and 2 <= odd_cnt <= 4:
            red_matrix.append(sorted(r5))
            break

    # ---------------------------------------------------------
    # 🔵 3. 蓝球 5 路诸侯实体化
    # ---------------------------------------------------------
    print("正在装配蓝球防守网...")
    recent_24_blues = df.tail(24).iloc[:, -1].values.tolist()
    blue_counts = Counter(recent_24_blues)

    b_A_cold = [b for b in range(1, 17) if b not in recent_24_blues]  # 极冷号
    b_A = random.choice(b_A_cold) if b_A_cold else blue_counts.most_common()[-1][0]

    b_B_hot = blue_counts.most_common(1)[0][0]  # 极热号

    b_Markov = int(np.argmax(blue_markov[last_draw_blue][1:]) + 1)  # 马尔可夫推演号

    # 🎯 终极组装绑定
    final_blues = [
        b_A,  # 配注1
        b_B_hot,  # 配注2
        b_Markov,  # 配注3
        ai_top2,  # 配注4 (榜眼)
        ai_top1  # 配注5 (状元)
    ]

    blue_tags = ["策略A(极冷)", "策略B(极热)", "状态转移(马尔可夫)", "AI 榜眼(多维算力)", "👑 AI 状元(王牌底仓)"]
    red_tags = ["1. EMA 平滑追热", "2. 破冰冷号狙击", "3. Apriori关联阵", "4. 物理步长推演", "👑 5. 宏观黄金防守"]

    # ---------------------------------------------------------
    # 🏆 4. 华丽输出
    # ---------------------------------------------------------
    print("\n================= 🏆 V3.0 降维打击预测矩阵 🏆 =================")

    # 💡 这是一个专门解决中英混排、Emoji 混合对齐的小神技
    def pad_str(text, target_width=22):
        display_width = 0
        for char in text:
            # 判断字符范围：如果是中文或Emoji（宽字符），视觉宽度算 2，英文算 1
            if '\u4e00' <= char <= '\u9fff' or ord(char) > 1000:
                display_width += 2
            else:
                display_width += 1
        # 计算差额并用空格补齐
        return text + " " * max(0, target_width - display_width)

    # 按照老板要求，调整了第 5 组的皇冠位置 👑
    blue_tags = ["策略A(极冷)", "策略B(极热)", "状态转移(马尔可夫)", "AI 榜眼(多维算力)", "👑 AI 状元(王牌底仓)"]
    red_tags = [" 1. EMA 平滑追热", " 2. 破冰冷号狙击", " 3. Apriori关联阵", " 4. 物理步长推演", " 5. 👑 宏观黄金防守"]

    for i in range(5):
        r_str = [str(x).zfill(2) for x in red_matrix[i]]
        b_str = str(final_blues[i]).zfill(2)
        # 用我们的神技函数替代原来的原生 <16 对齐
        aligned_tag = pad_str(red_tags[i], target_width=20)
        print(f"[{aligned_tag}] -> 🔴 {r_str}  |  🔵 [{b_str}] {blue_tags[i]}")
    print("=================================================================")

    print("\n📋 【纯净复制版】 (红球 + 蓝球)")
    print("-----------------------------------")
    for i in range(5):
        clean_r = " ".join([str(x).zfill(2) for x in red_matrix[i]])
        clean_b = str(final_blues[i]).zfill(2)
        print(f"{clean_r} + {clean_b}")
    print("-----------------------------------\n")


if __name__ == '__main__':
    generate_v3_numbers()