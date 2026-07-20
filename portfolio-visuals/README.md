# Portfolio Visuals — EE-칩 검증 시각화 3종 세트

IB 수학 EE("시리즈 RLC 회로의 damped oscillation")와 Tiny Tapeout 칩 프로젝트("Power-Aware Gray Code Counter")를 연결해서 보여주는 시각 자료. 대학 면접 데모, EE 부록, 포트폴리오용.

## 1. rlc-simulator.html — RLC 인터랙티브 시뮬레이터

**용도**: 면접에서 노트북으로 바로 시연. 인터넷 없이 브라우저로 더블클릭해서 열면 끝.

R/L/C 슬라이더를 움직이면 커패시터 전압의 감쇠 진동이 실시간으로 바뀐다. 댐핑비 ζ, 감쇠 유형(underdamped/critically damped/overdamped), 정착시간, 고유진동수가 자동 계산된다. 수식(2차 미분방정식, ζ 공식)도 화면에 표시됨.

**데모 순서 제안**: R을 낮은 값(underdamped, 진동함) → 200Ω 근처(critically damped) → 높은 값(overdamped)으로 움직이면서 "R이 클수록 진동이 억제된다"를 직접 보여주기. 이게 "칩의 전력망 저항이 클수록 스위칭 노이즈가 빨리 죽는다"는 얘기로 자연스럽게 이어짐.

## 2. waveform-verification.png (+ generate_waveform.py)

**용도**: 칩이 실제로 어떻게 동작하는지 보여주는 근거 자료.

이진 카운터(uio_out)와 그레이코드(uo_out) 출력을 클럭 사이클별 비트 파형으로 그린 것. 이진 카운터는 7→8로 넘어갈 때 4비트가 동시에 바뀌는 반면, 그레이코드는 모든 전환에서 항상 정확히 1비트만 바뀐다는 걸 시각적으로 보여줌. `test/test.py`(통과한 cocotb 테스트)가 검증한 것과 동일한 카운터 로직으로 계산해서 그림.

라이브 데모로 실제 파형 덤프를 직접 보여주고 싶으면 `gtkwave-setup.md` 참고 (`test/tb.fst`를 GTKWave로 열기).

## 3. ee-chip-connection.png (+ generate_ee_chip_connection.py)

**용도**: EE(이론)와 칩(구현)이 같은 물리 현상으로 연결된다는 걸 한 장으로 정리.

- 위: 이진 vs 그레이코드의 누적 스위칭 횟수 (256스텝 기준 510 vs 256, 49.8% 감소 — `tt-switching-analyzer`와 동일한 계산)
- 아래: 그 스위칭이 만드는 전류 스파이크(di/dt)가 RLC 감쇠진동(전압 링잉)으로 이어진다는 개념도. 그림에 명시했듯 실제 결합 시뮬레이션이 아니라 인과관계를 보여주는 개념적 예시임 — 면접에서 질문받으면 이 부분은 "개념적 연결이고, 실측 결합 시뮬레이션은 아니다"라고 정직하게 답할 것.

## 재생성 방법

```bash
cd portfolio-visuals
../.venv/bin/python3 generate_waveform.py
../.venv/bin/python3 generate_ee_chip_connection.py
```
