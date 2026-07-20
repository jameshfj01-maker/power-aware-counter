# Power-Aware Gray Code Counter — 프로젝트 여정 기록

자소서/포트폴리오용 초안. 사실 확인된 것과 아직 검증 안 된 것을 구분해서 적음 — 과장 없이 그대로 쓸 수 있게.

## 1. 무엇을 만들었나

Tiny Tapeout SKY26c 셔틀에 제출하는 실제 ASIC(주문형 반도체) 프로젝트. 8비트 카운터를 매 클럭 증가시키되, 출력을 이진수가 아니라 **그레이코드**로 변환해서 내보낸다. 그레이코드는 값이 바뀔 때 항상 정확히 1비트만 바뀌는 성질이 있어서, 여러 비트가 동시에 스위칭될 때 생기는 전력망 노이즈(di/dt)를 줄인다.

- 저장소: [power-aware-counter](https://github.com/jameshfj01-maker/power-aware-counter)
- 회로: [`src/project.v`](../src/project.v) — `binary_count`를 세고, `gray_count = binary_count ^ (binary_count >> 1)`로 변환

## 2. 기술적 문제 해결 과정

### 문제 1 — RTL 레이스 컨디션
cocotb 테스트가 "cycle 0 binary mismatch"로 실패. 원인은 Icarus Verilog에서 `await ClockCycles(dut.clk, 1)` 직후 non-blocking assignment(`<=`)로 갱신되는 레지스터 값을, 델타 사이클 갱신이 끝나기 전에 읽어버리는 레이스 컨디션. `Timer(1, unit="ns")`를 추가해서 한 틱 여유를 줘서 해결. (커밋 `b3f3312`)

### 문제 2 — 게이트레벨 타이밍 이슈
RTL 시뮬레이션은 통과했지만, 합성 후 게이트레벨 시뮬레이션(`gl_test`, 실제 스탠다드 셀 지연 포함)에서 다시 실패. RTL에서 충분했던 1ns 여유가 게이트레벨(`UNIT_DELAY=#1`)에서는 부족했던 것 — 실제 합성된 셀(플립플롭, 버퍼)들이 진짜 지연을 갖기 때문. `SETTLE_TIME`을 100ns로 늘려서 해결. (커밋 `171c6ec`) CI(test/gds/gl_test/precheck/viewer) 전부 통과.

### 테스트 커버리지 추가
0xFF→0x00 wraparound, `ena=0`일 때 카운터가 멈추는지 검증하는 테스트 2개 추가. (커밋 `c462a75`)

## 3. 실측 검증 — "주장"이 아니라 "숫자"로

그레이코드가 스위칭을 줄인다는 설계 의도를, 실제로 계산해서 증명함:

```
이진 카운터: 510회 스위칭 (8비트, 256스텝 전체 사이클, 스텝당 평균 1.992비트)
그레이코드:  256회 스위칭 (스텝당 정확히 1비트)
→ 스위칭 49.8% 감소
```

이 숫자는 디지털 로직의 확정적 성질이라 시뮬레이션이든 실제 칩이든 항상 재현돼야 한다. 계산 스크립트([`analysis/switching_activity.py`](../analysis/switching_activity.py))를 실제로 실행해서 검증했고, 그래프([`analysis/switching_comparison.png`](../analysis/switching_comparison.png))로도 정리했다.

## 4. 오픈소스 도구로 일반화

이 실측 로직을 "내 칩 전용"이 아니라 Tiny Tapeout 데모보드에 꽂힌 아무 프로젝트에나 쓸 수 있는 범용 도구로 만들어서 별도 저장소로 공개했다: [tt-switching-analyzer](https://github.com/jameshfj01-maker/tt-switching-analyzer). pip으로 설치 가능하고, 유닛 테스트와 CI를 갖췄다.

## 5. 정직한 현재 상태 (2026-07-20 기준)

**확정적으로 검증된 것:**
- RTL/게이트레벨 시뮬레이션 전부 통과 (실제 CI 로그로 확인)
- 스위칭 49.8% 감소 (실행해서 확인한 숫자, 디지털 로직 상 항상 성립)
- tt-switching-analyzer 코드 동작 (유닛 테스트 + CI 통과)

**아직 검증되지 않은 것 (하드웨어 도착 전이라 확인 불가):**
- 실제 칩에서의 동작 (`hardware/hardware_test.py` — SDK 소스코드까지 확인해서 작성했지만 실행은 못 해봄)
- 오픈소스 도구의 커뮤니티 반응 (아직 공유 전, 스타/포크/사용 사례 0)

이 구분은 중요하다 — "실측했다"는 사실이고, "커뮤니티에 임팩트를 줬다"는 아직 사실이 아니다. 자소서에는 검증된 것만 단정적으로 쓰고, 나머지는 "진행 중" 또는 "공개했다(released)"로 표현하는 게 정직하다.

## 6. 협업 방식에 대한 성찰

AI(Claude Code)와 함께 작업하면서 배운 것 하나: AI가 코드를 대신 빠르게 완성해주는 건 "활동을 만드는 것" 자체엔 효율적이지만, 그 과정에서 정작 나 자신은 아무것도 배우지 못한다는 걸 깨달았다. power-aware-counter의 후반 작업(하드웨어 검증 코드, 패키징, 테스트)은 내가 다른 일을 하는 동안 AI가 자율적으로 완료한 것이었는데, 결과물은 얻었지만 그 과정에서 배운 게 거의 없었다.

그래서 다음 개인 프로젝트(작은 CPU 설계)는 의도적으로 협업 방식을 바꾸기로 했다 — AI에게 답을 대신 만들어달라고 하지 않고, 개념을 설명받고 직접 구현하는 방식으로. 도구를 얼마나 빨리 쓰느냐보다, 언제 도구에 맡기고 언제 직접 해야 하는지를 판단하는 것 자체가 중요하다는 걸 이번에 알게 됐다.

## 7. 앞으로 남은 일

- 데모보드 구매 + 칩 도착 후 `hardware/hardware_test.py`로 실물 검증
- tt-switching-analyzer를 Tiny Tapeout Discord/포럼에 공유
- (진행 중) 대학 연구실 멘토링 이메일 응답 대기
