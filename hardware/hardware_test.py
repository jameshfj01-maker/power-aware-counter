# Tiny Tapeout 데모보드에서 실제 칩을 검증하는 스크립트.
# test/test.py(시뮬레이션)의 테스트 케이스를 실물 칩에 대해 그대로 재현한다.
#
# TinyTapeout/tt-micropython-firmware의 공식 예제
# (src/examples/tt_um_factory_test/tt_um_factory_test.py)와
# ttboard/cocotb/dut.py 소스코드를 GitHub에서 직접 읽고 작성함 (2026-07-20).
# 여전히 실제 데모보드로 실행은 못 해봤지만, 짐작이 아니라 확인된 API를 씀.
#
# 확인된 사실 두 가지:
# 1. 신호 값은 항상 .value로 읽는다 (dut.uo_out.value == x). .value 없이
#    바로 비교하면 Pin 객체와 정수를 비교하는 셈이라 항상 실패한다.
# 2. dut.ena는 NoopSignal이다 (ttboard/cocotb/dut.py 주석: "ena may be
#    used in existing tests, does nothing"). 즉 실제 칩에서는 ena 핀을
#    소프트웨어로 독립 제어할 방법이 SDK에 없다 (프로젝트 선택/해제에만
#    종속됨). 그래서 test_ena_low는 실물에서 재현 불가 — 시뮬레이션
#    test/test.py에서만 검증되는 케이스로 남긴다.

import gc

import microcotb as cocotb
from microcotb.clock import Clock
from microcotb.triggers import ClockCycles
import ttboard.cocotb.dut
from ttboard.demoboard import DemoBoard
from ttboard.mode import RPMode

gc.collect()

PROJECT_NAME = "tt_um_jameshfj01maker_power_aware_counter"


def to_gray(n):
    return n ^ (n >> 1)


async def reset(dut):
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    clock = Clock(dut.clk, 2, units="us")
    cocotb.start_soon(clock.start())

    await reset(dut)
    assert dut.uo_out.value == to_gray(0), f"reset 직후 gray 출력이 0이 아님: {dut.uo_out.value}"
    assert dut.uio_out.value == 0, f"reset 직후 binary 출력이 0이 아님: {dut.uio_out.value}"

    dut._log.info("Enable counting")
    dut.ui_in.value = 1

    expected_binary = 0
    for i in range(20):
        await ClockCycles(dut.clk, 1)
        expected_binary = (expected_binary + 1) & 0xFF
        expected_gray = to_gray(expected_binary)
        assert dut.uio_out.value == expected_binary, f"cycle {i} binary mismatch: {dut.uio_out.value} != {expected_binary}"
        assert dut.uo_out.value == expected_gray, f"cycle {i} gray mismatch: {dut.uo_out.value} != {expected_gray}"

    dut._log.info("Disable counting, value should hold")
    dut.ui_in.value = 0
    held_binary = expected_binary
    await ClockCycles(dut.clk, 5)
    assert dut.uio_out.value == held_binary
    assert dut.uo_out.value == to_gray(held_binary)

    dut._log.info("All checks passed")


@cocotb.test()
async def test_wraparound(dut):
    dut._log.info("Wraparound test: counter must roll over 0xFF -> 0x00")

    clock = Clock(dut.clk, 2, units="us")
    cocotb.start_soon(clock.start())

    await reset(dut)
    dut.ui_in.value = 1

    expected_binary = 0
    for i in range(256):
        await ClockCycles(dut.clk, 1)
        expected_binary = (expected_binary + 1) & 0xFF
        assert dut.uio_out.value == expected_binary, f"wraparound cycle {i} binary mismatch"
        assert dut.uo_out.value == to_gray(expected_binary), f"wraparound cycle {i} gray mismatch"

    assert expected_binary == 0
    dut._log.info("Wraparound checks passed")


# test_ena_low는 여기 없음 - 위 설명대로 실물 칩에서 재현 불가 (dut.ena가
# NoopSignal). ena=0 동작 검증은 test/test.py(시뮬레이션)가 유일한 근거.


def main():
    tt = DemoBoard.get()
    getattr(tt.shuttle, PROJECT_NAME).enable()

    if tt.mode != RPMode.ASIC_RP_CONTROL:
        tt.mode = RPMode.ASIC_RP_CONTROL

    tt.uio_oe_pico.value = 0  # uio는 칩이 출력하므로 RP2040 쪽은 입력으로

    dut = ttboard.cocotb.dut.DUT()
    runner = cocotb.get_runner(__name__)
    dut._log.info(f"enabled {PROJECT_NAME}, running tests")
    runner.test(dut)
    return runner


if __name__ == "__main__":
    main()
