# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


def to_gray(n):
    return n ^ (n >> 1)


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # 리셋 직후엔 카운터가 0이어야 함
    assert dut.uo_out.value == to_gray(0)
    assert dut.uio_out.value == 0

    dut._log.info("Enable counting")
    dut.ui_in.value = 1  # count enable = 1

    expected_binary = 0
    for i in range(20):
        await ClockCycles(dut.clk, 1)
        expected_binary = (expected_binary + 1) & 0xFF
        expected_gray = to_gray(expected_binary)
        assert dut.uio_out.value == expected_binary, \
            f"cycle {i}: binary_count 예상 {expected_binary}, 실제 {int(dut.uio_out.value)}"
        assert dut.uo_out.value == expected_gray, \
            f"cycle {i}: gray_count 예상 {expected_gray}, 실제 {int(dut.uo_out.value)}"

    dut._log.info("Disable counting, value should hold")
    dut.ui_in.value = 0
    held_binary = expected_binary
    await
