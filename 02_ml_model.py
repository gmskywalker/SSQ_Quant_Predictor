import numpy as np
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from data_engine import load_data, build_advanced_blue_windows


def train_and_predict_v3():
    print("============== 🧠 启动 V3.0 AI 超级球探中心 ==============")

    # 1. 调用你刚写好的超级引擎，获取高维特征集 (X: 5个维度, Y: 1-16的真实号码)
    X, Y = build_advanced_blue_windows(total_lookback=1000, window_size=25)

    if len(X) == 0:
        print("❌ 特征集为空，请检查数据引擎。")
        return

    print(f"🔬 成功加载 {len(X)} 组历史高维特征矩阵。正在训练 16 分类概率网...")

    # 2. 训练多分类随机森林 (参数拉满，增加树的数量和深度)
    clf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    clf.fit(X, Y)

    # 3. 提取“真正下一期”的实时环境特征
    # 我们需要截取最近 25 期的真实开奖蓝球，现场计算它的特征！
    df = load_data()
    recent_window = df.iloc[-25:, -1].values.astype(int)

    counts = Counter(recent_window)
    never_appeared = 16 - len(counts)
    max_freq = max(counts.values()) if counts else 0
    odds_count = sum(1 for x in recent_window if x % 2 != 0)
    bigs_count = sum(1 for x in recent_window if x >= 9)
    spans = [abs(recent_window[j] - recent_window[j - 1]) for j in range(1, len(recent_window))]
    avg_span = sum(spans) / len(spans) if spans else 0

    # 组装当前的 X
    next_X = np.array([[never_appeared, max_freq, odds_count, bigs_count, avg_span]])

    # 4. 预测所有 16 个球的概率分布！
    probabilities = clf.predict_proba(next_X)[0]
    classes = clf.classes_  # 获取模型学到的所有类别(真实的蓝球号码)

    # 将号码和概率绑定并排序
    prob_dict = {int(classes[i]): probabilities[i] for i in range(len(classes))}
    sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)

    # 5. 钦点状元和榜眼
    top1_ball, top1_prob = sorted_probs[0]
    top2_ball, top2_prob = sorted_probs[1]

    print("\n================ 📊 AI 蓝球 16 分类多维概率网预测 ==================")
    print(f"🥇 【状元签】: 蓝球 [{top1_ball:02d}] 胜率预测 -> {top1_prob * 100:.1f}%")
    print(f"🥈 【榜眼签】: 蓝球 [{top2_ball:02d}] 胜率预测 -> {top2_prob * 100:.1f}%")
    print(f"🥉 【探花签】: 蓝球 [{sorted_probs[2][0]:02d}] 胜率预测 -> {sorted_probs[2][1] * 100:.1f}%")
    print("------------------------------------------------------------------")

    # 6. 把指令写进小纸条，传给组装车间
    with open('ai_blue_picks.txt', 'w') as f:
        f.write(f"{top1_ball},{top2_ball}")
    print("✅ AI 预测完毕！已将 [状元, 榜眼] 指令写入 ai_blue_picks.txt，准备发往总装车间！")


if __name__ == '__main__':
    train_and_predict_v3()