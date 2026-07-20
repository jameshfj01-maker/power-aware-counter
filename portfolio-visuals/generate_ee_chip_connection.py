# EE(RLC 감쇠진동 이론)와 칩(그레이코드 스위칭 감소) 프로젝트를 하나의 그림으로 연결.
# 위: 이진 vs 그레이코드의 누적 스위칭 횟수 (tt-switching-analyzer로 계산한 것과 동일 데이터)
# 아래: 스위칭이 만드는 전류 스파이크가 RLC 감쇠진동(전압 링잉)으로 이어진다는 개념도
#
# 아래 패널은 실제로 결합 시뮬레이션을 돌린 게 아니라, "스위칭 비트 수가 많을수록
# di/dt 임펄스가 크고, 그래서 RLC 응답의 초기 진폭도 크다"는 인과관계를
# 같은 감쇠진동 방정식(rlc-simulator.html과 동일 공식)으로 개념적으로 보여주는 것.
# 그렇게 라벨을 명확히 붙여서 과장하지 않는다.

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from switching_activity import count_transitions, to_gray  # noqa: E402

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def cumulative_transitions(width=8):
    n = 1 << width
    binary_seq = list(range(n)) + [0]
    gray_seq = [to_gray(v) for v in binary_seq]
    b_steps = count_transitions(binary_seq)
    g_steps = count_transitions(gray_seq)
    b_cum, g_cum = [0], [0]
    for s in b_steps:
        b_cum.append(b_cum[-1] + s)
    for s in g_steps:
        g_cum.append(g_cum[-1] + s)
    return b_cum, g_cum


def rlc_response(t, zeta, w0, v0):
    import math
    if zeta < 1:
        wd = w0 * math.sqrt(1 - zeta * zeta)
        return v0 * math.exp(-zeta * w0 * t) * (
            math.cos(wd * t) + (zeta * w0 / wd) * math.sin(wd * t)
        )
    return v0 * math.exp(-w0 * t)


def main():
    b_cum, g_cum = cumulative_transitions()
    reduction = (1 - g_cum[-1] / b_cum[-1]) * 100

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(9, 8))

    # --- top: cumulative switching ---
    ax_top.step(range(len(b_cum)), b_cum, where="post", color="#d9534f", label=f"binary counter (total {b_cum[-1]})")
    ax_top.step(range(len(g_cum)), g_cum, where="post", color="#5cb85c", label=f"gray code (total {g_cum[-1]})")
    ax_top.set_xlabel("clock cycle (0–256, full 8-bit cycle)")
    ax_top.set_ylabel("cumulative bit transitions")
    ax_top.set_title(f"Switching activity: binary vs gray code  →  {reduction:.1f}% reduction")
    ax_top.legend(loc="upper left")
    ax_top.grid(alpha=0.2)

    # --- bottom: conceptual RLC ringing from switching-induced di/dt ---
    import numpy as np
    zeta, w0 = 0.12, 2000  # illustrative PDN-like values
    t = np.linspace(0, 0.008, 800)
    avg_binary = b_cum[-1] / 256  # ~1.992
    avg_gray = g_cum[-1] / 256    # 1.0
    v_binary = [rlc_response(tt, zeta, w0, avg_binary) for tt in t]
    v_gray = [rlc_response(tt, zeta, w0, avg_gray) for tt in t]

    ax_bot.plot(t * 1000, v_binary, color="#d9534f", label="binary: larger di/dt kick → larger ringing")
    ax_bot.plot(t * 1000, v_gray, color="#5cb85c", label="gray code: smaller di/dt kick → smaller ringing")
    ax_bot.axhline(0, color="#999999", linewidth=0.8)
    ax_bot.set_xlabel("time (ms)")
    ax_bot.set_ylabel("PDN voltage ringing\n(conceptual, arb. units)")
    ax_bot.set_title("Switching → di/dt spike → RLC damped oscillation (conceptual illustration)")
    ax_bot.legend(loc="upper right")
    ax_bot.grid(alpha=0.2)
    ax_bot.text(
        0.5, -0.32,
        "note: impulse scaled by average bits-switched per cycle — illustrates the causal link,\n"
        "not a co-simulated EM/circuit result.",
        transform=ax_bot.transAxes, ha="center", fontsize=8, color="#777777", style="italic",
    )

    fig.suptitle("From EE theory to chip design: why gray code reduces power-delivery noise", fontsize=13, y=0.99)
    fig.tight_layout(rect=[0, 0.05, 1, 0.96])
    fig.subplots_adjust(hspace=0.55)
    fig.savefig("ee-chip-connection.png", dpi=150)
    print("저장됨: ee-chip-connection.png")


if __name__ == "__main__":
    main()
