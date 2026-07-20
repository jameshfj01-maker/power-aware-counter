# GTKWave로 직접 파형 보기 (선택, 라이브 데모용)

`test/tb.fst`는 실제 시뮬레이션 파형 덤프다. `make`로 재생성 가능(`test/` 안에서 `export PATH="$HOME/.local/bin:$PATH" && make`).

1. `gtkwave test/tb.fst` 로 열기
2. 왼쪽 트리에서 `tb > user_project` 선택
3. 아래 순서로 신호 추가(더블클릭 또는 드래그): `clk`, `ui_in`, `uio_out`, `uo_out`
4. `uio_out`, `uo_out`은 우클릭 → Data Format → Binary 로 바꾸면 비트별로 보임
5. 시간 범위를 초반 몇 클럭(0 ~ 300000ns 정도, `test_project`의 카운팅 시작 구간)으로 확대
6. `uio_out`이 `0111 -> 1000`(7->8)으로 넘어가는 지점을 찾아서 하이라이트 — 4비트가 동시에 바뀌는 걸 보여주는 가장 극적인 순간
