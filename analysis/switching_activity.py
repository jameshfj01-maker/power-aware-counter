# 그레이코드 카운터와 이진 카운터의 비트 스위칭 횟수를 계산/비교하는 스크립트.
#
# 지금 당장(하드웨어 없이): generate_reference()가 0~255 전체 카운트 사이클에 대한
# 이론적 스위칭 횟수를 계산한다. 디지털 로직의 확정적 성질이라 시뮬레이션이나
# 실제 칩에서 측정한 값과 항상 정확히 일치해야 한다.
#
# 칩 도착 후: hardware/hardware_test.py 로 캡처한 실제 uo_out/uio_out 값을
# measure_from_samples()에 넣으면, "이론값이 실리콘에서도 정확히 맞았다"를
# 실측으로 증명할 수 있다.

WIDTH = 8


def to_gray(n):
    return n ^ (n >> 1)


def popcount(n):
    return bin(n).count("1")


def count_transitions(sequence):
    return [popcount(a ^ b) for a, b in zip(sequence, sequence[1:])]


def generate_reference(width=WIDTH):
    n = 1 << width
    binary_seq = list(range(n)) + [0]  # wraparound 스텝까지 포함
    gray_seq = [to_gray(v) for v in binary_seq]

    binary_steps = count_transitions(binary_seq)
    gray_steps = count_transitions(gray_seq)

    return {
        "steps": len(binary_steps),
        "binary_total": sum(binary_steps),
        "gray_total": sum(gray_steps),
        "binary_avg": sum(binary_steps) / len(binary_steps),
        "gray_avg": sum(gray_steps) / len(gray_steps),
    }


def measure_from_samples(binary_samples, gray_samples):
    binary_steps = count_transitions(binary_samples)
    gray_steps = count_transitions(gray_samples)
    return {
        "steps": len(binary_steps),
        "binary_total": sum(binary_steps),
        "gray_total": sum(gray_steps),
        "binary_avg": sum(binary_steps) / len(binary_steps) if binary_steps else 0,
        "gray_avg": sum(gray_steps) / len(gray_steps) if gray_steps else 0,
    }


def report(result, label="결과"):
    reduction = (1 - result["gray_total"] / result["binary_total"]) * 100
    print(f"--- {label} ---")
    print(f"측정 스텝 수: {result['steps']}")
    print(f"이진 카운터 총 스위칭: {result['binary_total']} (스텝당 평균 {result['binary_avg']:.3f}비트)")
    print(f"그레이코드 총 스위칭: {result['gray_total']} (스텝당 평균 {result['gray_avg']:.3f}비트)")
    print(f"스위칭 감소율: {reduction:.1f}%")
    return reduction


if __name__ == "__main__":
    ref = generate_reference()
    report(ref, label="이론값 (0~255 전체 사이클, 8비트)")
