# SPDX-FileCopyrightText: © 2026 Major Brinson / TrueSite Technologies
# SPDX-License-Identifier: Apache-2.0
"""ADAMA-1 plasticity core — does a synapse actually strengthen?"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

Q        = 16
W_CEIL   = 20 << Q          # 0x00140000
W_FLOOR  = 3276             # 0x00000CCC
OP_LTP   = 1
OP_LTD   = 2


async def wr(dut, addr, val):
    dut.ui_in.value = 0x80 | (addr & 0x0F)
    dut.uio_in.value = val
    await ClockCycles(dut.clk, 2)
    dut.ui_in.value = 0x00
    await ClockCycles(dut.clk, 1)


async def set_weight(dut, value):
    for i in range(4):
        await wr(dut, i, (value >> (8 * i)) & 0xFF)


async def set_op(dut, op):
    await wr(dut, 4, op)


async def read_weight(dut):
    v = 0
    for i in range(4):
        dut.ui_in.value = i
        await Timer(1, unit="ns")
        v |= (int(dut.uo_out.value) & 0xFF) << (8 * i)
    return v


@cocotb.test()
async def test_ltp_strengthens(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    await set_weight(dut, 1 << Q)          # 1.0
    before = await read_weight(dut)
    assert before == (1 << Q), f"write failed: read 0x{before:08x}"

    await set_op(dut, OP_LTP)
    await Timer(1, unit="ns")
    after = await read_weight(dut)
    assert after > before, f"LTP did not strengthen: 0x{before:08x} -> 0x{after:08x}"
    dut._log.info(f"LTP: 0x{before:08x} -> 0x{after:08x}")


@cocotb.test()
async def test_ltd_weakens(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    await set_weight(dut, 2 << Q)          # 2.0
    await set_op(dut, OP_LTD)
    await Timer(1, unit="ns")
    after = await read_weight(dut)
    assert after < (2 << Q), f"LTD did not weaken: 0x{after:08x}"
    dut._log.info(f"LTD: 0x{2 << Q:08x} -> 0x{after:08x}")


@cocotb.test()
async def test_ceiling_saturates(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    await set_weight(dut, W_CEIL)           # 20.0 = ceiling
    await set_op(dut, OP_LTP)
    await Timer(1, unit="ns")
    after = await read_weight(dut)
    assert after == W_CEIL, f"weight passed the ceiling: 0x{after:08x}"
    dut.ui_in.value = 5
    await Timer(1, unit="ns")
    status = int(dut.uo_out.value)
    assert (status >> 3) & 1, f"satur flag not set, status=0x{status:02x}"
    dut._log.info(f"ceiling held at 0x{after:08x}, status 0x{status:02x}")
