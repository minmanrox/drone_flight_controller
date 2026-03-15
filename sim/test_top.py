# sim/cocotb/test_top.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

CLK_PERIOD_NS = 40  # 25 MHz
PERIOD_CYCLES = 500_000  # 20 ms @ 25 MHz
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


async def drive_pwm_input(clk, signal, high_cycles, low_cycles, periods):
    """Drive 'signal' with 'periods' PWM periods at given high/low cycle counts."""
    for _ in range(periods):
        signal.value = 1
        for _ in range(high_cycles):
            await RisingEdge(clk)
        signal.value = 0
        for _ in range(low_cycles):
            await RisingEdge(clk)


async def drive_multiple_pwms(clk, pwm_cfgs, periods):
    """
    Drive multiple PWM inputs in parallel.

    Parameters
    ----------
    clk : handle
        Clock signal (e.g. dut.clk).
    pwm_cfgs : dict or list
        If dict: {signal_handle: (high_cycles, low_cycles), ...}
        If list: [(signal_handle, high_cycles, low_cycles), ...]
    periods : int
        Number of PWM periods to drive for each signal.
    """

    tasks = []

    if isinstance(pwm_cfgs, dict):
        for sig, (high_cycles, low_cycles) in pwm_cfgs.items():
            tasks.append(
                cocotb.start_soon(drive_pwm_input(clk, sig, high_cycles, low_cycles, periods))
            )
    else:
        for sig, high_cycles, low_cycles in pwm_cfgs:
            tasks.append(
                cocotb.start_soon(drive_pwm_input(clk, sig, high_cycles, low_cycles, periods))
            )

    # Wait for all PWM drivers to finish
    for t in tasks:
        await t


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


@cocotb.test(skip=True)
async def test_arm_gates_throttle(dut):
    """With throttle max: arm=0 → no PWM out; arm=1 → PWM present."""
    dut._log.warning("set CALIB_HOLD in system_params.vh to a small value (e.g. 2)")
    dut._log.info("Starting arm gating test")

    # Start 25 MHz clock
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())

    # Initialize inputs
    dut.arm_in.value = 0
    dut.calib_reset_button.value = 0
    dut.pwm_in1.value = 0
    dut.pwm_in2.value = 0
    dut.pwm_in3.value = 0
    dut.pwm_in4.value = 0

    # Let DUT settle / complete calibration
    await Timer(2, unit="ms")

    # Define max and min throttle input PWM
    high_cycles_max = 50_000
    low_cycles_max  = PERIOD_CYCLES - high_cycles_max
    high_cycles_min = 25_000
    low_cycles_min  = PERIOD_CYCLES - high_cycles_min

    # Phase 1: arm=0, drive max throttle, output should remain effectively off
    dut._log.info("Phase 1: arm=0, throttle=max")

    # drive throttle and arm (for min) simultaneously
    pwm_cfgs = {
        dut.pwm_in1: (high_cycles_max, low_cycles_max),
        dut.arm_in: (high_cycles_min, low_cycles_min),
    }
    await drive_multiple_pwms(dut.clk, pwm_cfgs, 1)
    assert(dut.arm_led.value == 0)

    # Measure pwm_out1 duty over a few periods
    duty_disarmed = await measure_pwm_duty(dut, PERIOD_CYCLES)
    d1_disarmed = duty_disarmed[1]
    dut._log.info(f"Disarmed duty pwm_out1={d1_disarmed:.4f}")

    # Expect very low duty (ideally 0); allow tiny glitches if any
    assert d1_disarmed < 0.01, "pwm_out1 should be off or near 0 when arm=0"

    # Phase 2: arm=1, same max throttle, now PWM should be present
    dut._log.info("Phase 2: arm=1, throttle=max")

    # drive throttle and arm (for max) simultaneously
    pwm_cfgs = {
        dut.pwm_in1: (high_cycles_max, low_cycles_max),
        dut.arm_in: (high_cycles_max, low_cycles_max),
    }
    await drive_multiple_pwms(dut.clk, pwm_cfgs, 1)
    assert(dut.arm_led.value == 1)

    duty_armed = await measure_pwm_duty(dut, PERIOD_CYCLES)
    d1_armed = duty_armed[1]
    dut._log.info(f"Armed duty pwm_out1={d1_armed:.4f}")

    # Expect high pulse > 1.5ms
    assert d1_armed > 0.075, "pwm_out1 should be active when arm=1 and throttle=max"

    dut._log.info("Arm gating test PASSED")
