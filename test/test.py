# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

# Gate-level (post-synthesis) simulation runs with UNIT_DELAY=#1, so every
# standard cell (flip-flop, buffer, ...) between the clock edge and the
# output pins adds real delay. 1ns is only enough for RTL sim, where
# non-blocking assignments settle almost instantly. 100ns is a large margin
# under the 10us clock period but comfortably covers the gate-level delay chain.
SETTLE_TIME = 100


def to_gray(n):
    return n ^ (n >> 1)


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    await Timer(SETTLE_TIME, unit="ns")

    assert dut.uo_out.value == to_gray(0)
    assert dut.uio_out.value == 0

    dut._log.info("Enable counting")
    dut.ui_in.value = 1
    await Timer(SETTLE_TIME, unit="ns")

    expected_binary = 0
    for i in range(20):
        await ClockCycles(dut.clk, 1)
        await Timer(SETTLE_TIME, unit="ns")  # let the gate-level delay chain settle before reading
        expected_binary = (expected_binary + 1) & 0xFF
        expected_gray = to_gray(expected_binary)
        binary_msg = "cycle " + str(i) + " binary mismatch"
        gray_msg = "cycle " + str(i) + " gray mismatch"
        assert dut.uio_out.value == expected_binary, binary_msg
        assert dut.uo_out.value == expected_gray, gray_msg

    dut._log.info("Disable counting, value should hold")
    dut.ui_in.value = 0
    held_binary = expected_binary
    await ClockCycles(dut.clk, 5)
    await Timer(SETTLE_TIME, unit="ns")
    assert dut.uio_out.value == held_binary
    assert dut.uo_out.value == to_gray(held_binary)

    dut._log.info("All checks passed")
