import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock


CLK_PERIOD_NS = 40  # 25 MHz


async def send_pulse(dut, high_cycles: int):
    """Drive pwm_in high for high_cycles, then low, at 25 MHz."""
    dut.pwm_in1.value = 0
    await RisingEdge(dut.clk)

    dut.pwm_in1.value = 1
    for _ in range(high_cycles):
        await RisingEdge(dut.clk)
        assert(dut.r1.pwm_in.value == 1)
    dut.pwm_in1.value = 0

    # Give the DUT a couple of cycles to latch and compute
    for _ in range(5):
        await RisingEdge(dut.clk)


@cocotb.test()
async def test_basic_mapping(dut):
    """Check that longer pulse widths produce larger 'value'."""
    dut._log.info("Starting pwm_to_mix basic mapping test")
    pwm = dut.r1
    # dut._log.info(f"DUT has attributes: {dir(pwm)}")

    # Start 25 MHz clock
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    await RisingEdge(pwm.clk)
    assert(bool(dut.clk.value))
    assert(bool(pwm.clk.value))

    # Initialize inputs
    dut.pwm_in1.value = 0
    pwm.value.value = 0
    await Timer(100, unit="ns")

    # Convenience: 25 MHz counts for given pulse widths
    count_1ms   = 25_000
    count_1_5ms  = 37_500
    count_2ms   = 50_000

    # 1 ms pulse → near minimum value
    await send_pulse(dut, count_1ms)
    val_1ms = int(pwm.value.value)
    dut._log.info(f"value at 1 ms pulse: {val_1ms}")

    # 1.5 ms pulse → mid value
    await send_pulse(dut, count_1_5ms)
    val_15ms = int(dut.r1.value.value)
    dut._log.info(f"value at 1.5 ms pulse: {val_15ms}")

    # 2 ms pulse → near maximum value
    await send_pulse(dut, count_2ms)
    val_2ms = int(pwm.value.value)
    dut._log.info(f"value at 2 ms pulse: {val_2ms}")

    # Basic sanity checks
    assert 0 <= val_1ms <= 10, "1 ms should map near 0"
    assert val_1ms <= val_15ms <= val_2ms, "value must be monotonic with pulse width"
    assert val_2ms > 100, "2 ms should map to a significantly larger value"

    dut._log.info("pwm_to_mix basic mapping test PASSED")
