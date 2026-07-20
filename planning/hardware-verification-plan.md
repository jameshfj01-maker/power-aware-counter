# 칩 실물 검증 + 활동 강화 계획

## 현재 상황 요약 (2026-07-20 기준)

- **프로젝트**: "Power-Aware Gray Code Counter" — Tiny Tapeout SKY26c 셔틀 제출, 마감 2026-09-08
- **코드/CI 상태**: RTL 레이스 컨디션, 게이트레벨 타이밍 이슈 모두 해결. 테스트 커버리지(wraparound, ena=0) 추가 완료. CI(test/gds/gl_test/precheck/viewer) 전부 통과. 결제만 하면 제출 가능한 상태.
- **대학 연구실 멘토링**: 이메일로 컨택 완료, 결과 대기 중 (통제 불가능한 변수)
- **국제 과학경진대회(ISEF) / 논문 단독 출판 / IDEC 경진대회**: 시간·역량·일정 문제로 이번엔 제외
- **결론**: "칩+실측"만으론 상위권이지만 최상위 단정은 어려움. 아래 3개 축을 동시에 쌓아서 활동 완성도를 최대화하기로 함.

## 활동 강화 3축

1. **기술적 깊이 (실행 중)** — 칩을 실제로 검증하고 측정한 데이터
2. **검증 가능한 커뮤니티 임팩트 (신규)** — 실측 도구를 나만 쓰는 게 아니라 Tiny Tapeout 커뮤니티 전체가 쓸 수 있는 오픈소스 도구로 공개
3. **전문가 검증 (대기 중)** — 멘토링 응답 오면 진행, 안 와도 1·2번은 그대로 유효

## 작업 항목

### 1. microcotb 포팅
- **목표**: `test/test.py`의 cocotb 테스트를 실물 칩용으로 포팅
- **상태**: 완료, API 소스코드로 검증까지 마침 — [`hardware/hardware_test.py`](../hardware/hardware_test.py). 2026-07-20에 TinyTapeout/tt-micropython-firmware GitHub 소스(`demoboard.py`, `ttboard/cocotb/dut.py`, 공식 예제 `tt_um_factory_test.py`)를 직접 읽고 재작성함. 확인된 사실: ① 신호는 항상 `.value`로 읽어야 함(`dut.uo_out.value`, 없이 비교하면 항상 실패) ② `dut.ena`는 `NoopSignal`이라 실제 칩에서 ena를 소프트웨어로 독립 제어할 방법이 없음(소스 주석으로 확인) → `test_ena_low`는 실물 재현 불가능하다는 게 확정됨, 시뮬레이션 전용 테스트로 남김. 실제 데모보드 실행은 여전히 못 해봤지만 더 이상 짐작이 아니라 소스 확인된 상태.

### 2. 실측 스크립트 — 스위칭 횟수 측정
- **목표**: `uo_out`(그레이코드)과 `uio_out`(이진 카운터)의 비트 전환 횟수를 세어 비교
- **결과물**: "그레이코드가 이진 대비 스위칭을 몇 % 줄이는지"에 대한 실제 숫자
- **하드웨어 필요 여부**: 알고리즘 자체는 시뮬레이션 데이터로 지금 검증 가능. 실제 칩 값 읽기만 하드웨어 필요
- **상태**: 완료 — [`analysis/switching_activity.py`](../analysis/switching_activity.py). 실행 결과(8비트, 256스텝 전체 사이클): 이진 카운터 510회 스위칭(스텝당 평균 1.992비트) vs 그레이코드 256회(스텝당 정확히 1비트) → **스위칭 49.8% 감소**. 이건 디지털 로직의 확정적 성질이라 시뮬레이션·실제 칩 어디서 재현해도 동일해야 함. `measure_from_samples()`에 실제 칩에서 캡처한 값을 넣으면 이론값과 실측값 비교 가능.

### 3. 결과 시각화 스크립트
- **목표**: 측정 결과를 그래프로 정리 (막대그래프: 이진 vs 그레이코드 스위칭 횟수)
- **의존성**: 2번 데이터 형식 확정 후
- **상태**: 완료 — [`analysis/visualize_switching.py`](../analysis/visualize_switching.py). 실행하면 `analysis/switching_comparison.png` 생성 (총 스위칭 횟수 + 스텝당 평균 비교, 49.8% 감소 표시). `.venv`에 matplotlib 설치함 (`analysis/requirements.txt`).

### 4. config.ini 준비
- **목표**: 데모보드 프로젝트 선택/클럭 설정 자동화
- **상태**: 완료, 실제 기본 `config.ini` 스키마와 대조 확인함 — [`hardware/config.ini`](../hardware/config.ini). `clock_frequency`는 `[DEFAULT]`가 아니라 프로젝트별 섹션에 둬야 한다는 걸 실제 예시로 확인해서 수정함.

### 5. 오픈소스 도구 공개 (신규)
- **목표**: 2번 실측 스크립트를 "내 칩 전용"이 아니라 "TT 데모보드에 꽂힌 아무 프로젝트나 측정 가능한 범용 도구"로 일반화
- **결과물**: 공개 GitHub 저장소 + TT Discord/포럼 공유. 스타/포크/사용 사례가 검증 가능한 임팩트 지표가 됨
- **의존성**: 2번 완료 후
- **상태**: GitHub 공개 완료, 패키징/테스트/CI까지 갖춤 — https://github.com/jameshfj01-maker/tt-switching-analyzer . `core.py`(임의 신호 비교), `cli.py`, `ttboard_capture.py`(TinyTapeout 실제 SDK 소스로 검증, 실행은 미검증), `pyproject.toml`(pip 설치 가능), `tests/test_core.py`(유닛 테스트 6개, 통과), `.github/workflows/test.yml`(CI, 첫 실행부터 그린). 예제(`examples/gray_vs_binary.py`, 실행 검증 완료: 510 vs 256회, 49.8% 감소). **남은 것**: TT Discord/포럼 공유 — 내일 진행 예정 (본인 계정으로 직접).

## 진행 순서

1(완료) → 2 → 3, 4(병행 가능) → 5

## 칩 도착 후 남는 작업

- 데모보드 직접 구매 (store.tinytapeout.com)
- 준비한 스크립트 전체를 실제 칩에 연결해서 실행 및 보정
- 측정 결과 + 디버깅 여정 + 오픈소스 공개 반응까지 최종 문서로 정리
