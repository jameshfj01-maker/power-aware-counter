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


async def reset(dut):
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    await Timer(SETTLE_TIME, unit="ns")


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")
    await reset(dut)

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


@cocotb.test()
async def test_wraparound(dut):
    dut._log.info("Wraparound test: counter must roll over 0xFF -> 0x00")
    await reset(dut)

    dut.ui_in.value = 1
    await Timer(SETTLE_TIME, unit="ns")

    expected_binary = 0
    for i in range(256):
        await ClockCycles(dut.clk, 1)
        await Timer(SETTLE_TIME, unit="ns")
        expected_binary = (expected_binary + 1) & 0xFF
        expected_gray = to_gray(expected_binary)
        binary_msg = "wraparound cycle " + str(i) + " binary mismatch"
        gray_msg = "wraparound cycle " + str(i) + " gray mismatch"
        assert dut.uio_out.value == expected_binary, binary_msg
        assert dut.uo_out.value == expected_gray, gray_msg

    # After exactly 256 cycles from 0, the counter must have wrapped back to 0.
    assert expected_binary == 0
    assert dut.uio_out.value == 0
    assert dut.uo_out.value == to_gray(0)

    dut._log.info("Wraparound checks passed")


@cocotb.test()
async def test_ena_low(dut):
    dut._log.info("ena=0 test: counter must not advance while the design is not selected")
    await reset(dut)

    dut.ena.value = 0
    dut.ui_in.value = 1  # count-enable is on, but chip-enable (ena) is off
    await Timer(SETTLE_TIME, unit="ns")

    for i in range(10):
        await ClockCycles(dut.clk, 1)
        await Timer(SETTLE_TIME, unit="ns")
        binary_msg = "ena=0 cycle " + str(i) + ": counter should not advance"
        assert dut.uio_out.value == 0, binary_msg
        assert dut.uo_out.value == to_gray(0)

    dut._log.info("Re-enable design, counting should resume")
    dut.ena.value = 1
    await ClockCycles(dut.clk, 1)
    await Timer(SETTLE_TIME, unit="ns")
    assert dut.uio_out.value == 1
    assert dut.uo_out.value == to_gray(1)

    dut._log.info("ena=0 checks passed")
