# sim/cocotb/test_top.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

CLK_PERIOD_NS = 40  # 25 MHz
CALIB_CYCLES = 125_000 # UPDATE in system_params.vh - set lower to improve sim time

async def measure_pwm_duty(dut, cycles: int) -> dict[int, float]:
    """
    Measure duty cycle of pwm_out1..4 over 'cycles' rising edges of dut.clk.
    Returns a dict with fractional duty: {1: d1, 2: d2, 3: d3, 4: d4}.
    """

    # Counters for high time
    high_counts = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
    }

    for _ in range(cycles):
        await RisingEdge(dut.clk)
        high_counts[1] += int(dut.pwm_out1.value)
        high_counts[2] += int(dut.pwm_out2.value)
        high_counts[3] += int(dut.pwm_out3.value)
        high_counts[4] += int(dut.pwm_out4.value)

    duty = {ch: high_counts[ch] / cycles for ch in high_counts}
    return duty

@cocotb.test()
async def dummy_smoke_test(dut):
    """Simple smoke test: toggle inputs and run a few cycles."""
    dut._log.info("Starting dummy smoke test")

    # Initialize inputs
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.pwm_in1.value = 0
    dut.pwm_in2.value = 0
    dut.pwm_in3.value = 0
    dut.pwm_in4.value = 0
    dut.arm_in.value = 0
    dut.calib_reset_button.value = 0

    # Let things settle
    await Timer(1, unit="ns")

    # Apply a simple stimulus
    dut.arm_in.value = 1
    dut._log.info("Arm asserted")
    await RisingEdge(dut.clk)
    dut.arm_in.value = 0

    # Run for 100 clock cycles
    for i in range(100):
        await RisingEdge(dut.clk)
        dut._log.debug(f"Cycle {i}: pwm_out1={int(dut.pwm_out1.value)}")

    dut._log.info("Dummy smoke test completed")


@cocotb.test(skip=True)
async def test_calibration_sequence(dut):
    """Hold throttle low then high for 5s each and check calibration completes."""
    dut._log.warning("ENSURE CALIB_HOLD IN system_params.vh MATCHES CALIB_CYCLES IN test_top.py")
    dut._log.info("Starting top_module calibration sequence test")

    # Start 25 MHz clock
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())

    # Initialize inputs
    dut.arm_in.value = 0
    dut.calib_reset_button.value = 0
    dut.pwm_in1.value = 0
    dut.pwm_in2.value = 0
    dut.pwm_in3.value = 0
    dut.pwm_in4.value = 0

    # Let reset / initial logic settle
    await Timer(1, unit="ms")

    assert(int(dut.calibration_led.value) == 0)
    assert(int(dut.e1.calibration_state.value) == 0)
    min_calib_duties = await measure_pwm_duty(dut, CALIB_CYCLES)
    dut._log.info("Calibration phase 0 duty cycles:")
    print(min_calib_duties)

    assert(int(dut.e1.calibration_state.value) == 1)
    max_calib_duties = await measure_pwm_duty(dut, CALIB_CYCLES)
    dut._log.info("Calibration phase 1 duty cycles:")
    print(max_calib_duties)

    assert(int(dut.e1.calibration_state.value) == 2)
    dut._log.info("Finished calibration phase 1")

    for minDuty in min_calib_duties.keys():
        for maxDuty in max_calib_duties.keys():
            assert(min_calib_duties[minDuty] < max_calib_duties[maxDuty])

    assert(bool(dut.calibration_led.value))

    dut._log.info("Calibration sequence test completed")
