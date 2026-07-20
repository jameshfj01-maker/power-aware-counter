# switching_activity.py의 결과를 그래프로 만드는 스크립트.
# 포트폴리오/자소서에 바로 넣을 수 있는 PNG를 만든다.

import matplotlib.pyplot as plt

from switching_activity import generate_reference

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def plot_comparison(result, out_path="switching_comparison.png"):
    labels = ["이진 카운터", "그레이코드 카운터"]
    colors = ["#d9534f", "#5cb85c"]
    totals = [result["binary_total"], result["gray_total"]]
    averages = [result["binary_avg"], result["gray_avg"]]

    fig, axes = plt.subplots(1, 2, figsize=(9, 4))

    axes[0].bar(labels, totals, color=colors)
    axes[0].set_title(f"{result['steps']}스텝 총 스위칭 횟수")
    axes[0].set_ylabel("비트 전환 횟수")
    for i, v in enumerate(totals):
        axes[0].text(i, v + 5, str(v), ha="center")

    axes[1].bar(labels, averages, color=colors)
    axes[1].set_title("스텝당 평균 스위칭 횟수")
    axes[1].set_ylabel("비트")
    for i, v in enumerate(averages):
        axes[1].text(i, v + 0.03, f"{v:.2f}", ha="center")

    reduction = (1 - result["gray_total"] / result["binary_total"]) * 100
    fig.suptitle(f"Power-Aware Gray Code Counter: 스위칭 {reduction:.1f}% 감소")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"저장됨: {out_path}")


if __name__ == "__main__":
    result = generate_reference()
    plot_comparison(result)
