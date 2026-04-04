# sim/cocotb/test_top.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.utils import get_sim_time

CLK_PERIOD_NS = 40  # 25 MHz
PERIOD_CYCLES = 500_000  # 20 ms @ 25 MHz
CALIB_CYCLES = 500_000 # UPDATE in system_params.vh - set lower to improve sim time
HIGH_CYCLES_MAX = 50_000
LOW_CYCLES_MAX  = PERIOD_CYCLES - HIGH_CYCLES_MAX
HIGH_CYCLES_MIN = 25_000
LOW_CYCLES_MIN  = PERIOD_CYCLES - HIGH_CYCLES_MIN


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


@cocotb.test(skip=False)
async def test_calibration_sequence(dut):
    """Trigger calibration mechanism and confirm output matches expected."""
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

    dut.calib_reset_button.value = 1
    await Timer(10, unit="ms")
    dut.calib_reset_button.value = 0
    await RisingEdge(dut.clk)

    assert(int(dut.calibration_led.value) == 0)
    assert(int(dut.e1.calibration_state.value) == 0)
    max_calib_duties = await measure_pwm_duty(dut, CALIB_CYCLES)
    dut._log.info("Calibration phase 0 duty cycles:")
    print(max_calib_duties)
    dut._log.info(f"Finished phase 0 at sim time {get_sim_time(units='ns')}")

    await Timer(10, unit="ms")
    assert(int(dut.e1.calibration_state.value) == 1)
    min_calib_duties = await measure_pwm_duty(dut, CALIB_CYCLES)
    dut._log.info("Calibration phase 1 duty cycles:")
    print(min_calib_duties)

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

    # Expect minimum duty (ideally 0.05)
    assert d1_disarmed <= 0.05, "pwm_out1 should be near 0.05 when arm=0"

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


async def drive_controls(dut, throttle, pitch, roll, yaw, periods=1):
    """Set normalized control inputs in your preferred representation."""
    if throttle < 0 or throttle > 1:
        raise("drive_controls must be between 0 and 1")
    if pitch < 0 or pitch > 1:
        raise("drive_controls must be between 0 and 1")
    if roll < 0 or roll > 1:
        raise("drive_controls must be between 0 and 1")
    if yaw < 0 or yaw > 1:
        raise("drive_controls must be between 0 and 1")

    throttleCyclesHigh  = int(throttle  * (HIGH_CYCLES_MAX-HIGH_CYCLES_MIN) + HIGH_CYCLES_MIN)
    pitchCyclesHigh     = int(pitch     * (HIGH_CYCLES_MAX-HIGH_CYCLES_MIN) + HIGH_CYCLES_MIN)
    rollCyclesHigh      = int(roll      * (HIGH_CYCLES_MAX-HIGH_CYCLES_MIN) + HIGH_CYCLES_MIN)
    yawCyclesHigh       = int(yaw       * (HIGH_CYCLES_MAX-HIGH_CYCLES_MIN) + HIGH_CYCLES_MIN)

    pwm_cfgs = {
        dut.pwm_in1: (throttleCyclesHigh, PERIOD_CYCLES - throttleCyclesHigh),
        dut.pwm_in2: (yawCyclesHigh, PERIOD_CYCLES - yawCyclesHigh),
        dut.pwm_in3: (pitchCyclesHigh, PERIOD_CYCLES - pitchCyclesHigh),
        dut.pwm_in4: (rollCyclesHigh, PERIOD_CYCLES - rollCyclesHigh),
        dut.arm_in: (HIGH_CYCLES_MAX, LOW_CYCLES_MAX),
    }

    await drive_multiple_pwms(
        clk=dut.clk,
        pwm_cfgs=pwm_cfgs,
        periods=periods
    )


async def read_mixer_values(dut):
    """Sample current logic levels for the 4 PWM outputs."""
    return {
        "throttleRaw": str(dut.mx.throttle.value),
        "pitchRaw":    str(dut.mx.pitch.value),
        "rollRaw":     str(dut.mx.roll.value),
        "yawRaw":      str(dut.mx.yaw.value),
        "throttleInt": int(dut.mx.throttleSigned.value.to_signed()),
        "pitchInt":    int(dut.mx.pitchSigned.value.to_signed()),
        "rollInt":     int(dut.mx.rollSigned.value.to_signed()),
        "yawInt":      int(dut.mx.yawSigned.value.to_signed()),
        "m1":       str(dut.mx.motor1.value),
        "m2":       str(dut.mx.motor2.value),
        "m3":       str(dut.mx.motor3.value),
        "m4":       str(dut.mx.motor4.value),
    }


@cocotb.test(skip=True)
async def test_throttle_min_max(dut):
    """Throttle axis only: min and max, all other axes neutral."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())

    # Throttle minimum
    await drive_controls(dut, throttle=0, pitch=0.5, roll=0.5, yaw=0.5)
    levels = await read_mixer_values(dut)
    dut._log.debug(f"Levels (min): {levels}")

    min_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.debug(f"Duties (min): {min_duties}")
    for motor, duty in min_duties.items():
        assert duty > 0.07 and duty < 0.08, f"min_throttle motor {motor} duty out of range at {duty}"

    # Throttle maximum
    await drive_controls(dut, throttle=1, pitch=0.5, roll=0.5, yaw=0.5)
    levels = await read_mixer_values(dut)
    dut._log.debug(f"Levels (min): {levels}")
    max_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.debug(f"Duties (max): {max_duties}")
    for motor, duty in max_duties.items():
        assert duty > 0.08 and duty < 0.09, f"max_throttle motor {motor} duty out of range at {duty}"


@cocotb.test(skip=True)
async def test_pitch_min_max(dut):
    """Pitch axis only: min and max, all other axes neutral."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())

    # Pitch minimum
    dut._log.info("Driving pitch low (tilt backwards)")
    await drive_controls(dut, throttle=0.5, pitch=0, roll=0.5, yaw=0.5)
    levels = await read_mixer_values(dut)
    dut._log.info(f"Levels (min): {levels}")

    min_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.info(f"Duties (min): {min_duties}")
    # expect front motors (1, 2) high, rear motors (3, 4) low
    assert min_duties[1] == min_duties[2], f"Motors 1 ({min_duties[1]}) and 2 ({min_duties[2]}) not equal"
    assert min_duties[3] == min_duties[4], f"Motors 3 ({min_duties[3]}) and 4 ({min_duties[4]}) not equal"
    assert min_duties[1] >  min_duties[4], f"Front motors ({min_duties[1]}) not faster than rear motors ({min_duties[4]})"

    # Pitch maximum
    dut._log.info("Driving pitch high (tilt forwards)")
    await drive_controls(dut, throttle=0.5, pitch=1, roll=0.5, yaw=0.5)
    levels = await read_mixer_values(dut)
    dut._log.info(f"Levels (min): {levels}")
    max_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.info(f"Duties (max): {max_duties}")
    # expect front motors (1, 2) low, rear motors (3, 4) high
    assert max_duties[1] == max_duties[2], f"Motors 1 ({max_duties[1]}) and 2 ({max_duties[2]}) not equal"
    assert max_duties[3] == max_duties[4], f"Motors 3 ({max_duties[3]}) and 4 ({max_duties[4]}) not equal"
    assert max_duties[1] <  max_duties[4], f"Front motors ({max_duties[1]}) not slower than rear motors ({max_duties[4]})"


@cocotb.test(skip=True)
async def test_roll_min_max(dut):
    """Roll axis only: min and max, all other axes neutral."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())

    # Roll minimum
    dut._log.info("Driving roll low (tilt left)")
    await drive_controls(dut, throttle=0.5, pitch=0.5, roll=0, yaw=0.5)
    levels = await read_mixer_values(dut)
    dut._log.info(f"Levels (min): {levels}")

    min_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.info(f"Duties (min): {min_duties}")
    # expect left motors (1, 4) low, right motors (2, 3) high
    assert min_duties[1] == min_duties[4], f"Motors 1 ({min_duties[1]}) and 4 ({min_duties[4]}) not equal"
    assert min_duties[2] == min_duties[3], f"Motors 2 ({min_duties[2]}) and 3 ({min_duties[3]}) not equal"
    assert min_duties[1] <  min_duties[2], f"Right motors ({min_duties[2]}) not faster than left motors ({min_duties[1]})"

    # Roll maximum
    dut._log.info("Driving roll high (tilt right)")
    await drive_controls(dut, throttle=0.5, pitch=0.5, roll=1, yaw=0.5)
    levels = await read_mixer_values(dut)
    dut._log.info(f"Levels (min): {levels}")
    max_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.info(f"Duties (max): {max_duties}")
    # expect left motors (1, 4) high, right motors (2, 3) low
    assert max_duties[1] == max_duties[4], f"Motors 1 ({max_duties[1]}) and 4 ({max_duties[4]}) not equal"
    assert max_duties[2] == max_duties[3], f"Motors 2 ({max_duties[2]}) and 3 ({max_duties[3]}) not equal"
    assert max_duties[1] >  max_duties[2], f"Left motors ({max_duties[1]}) not faster than right motors ({max_duties[2]})"


@cocotb.test(skip=True)
async def test_yaw_min_max(dut):
    """Yaw axis only: min and max, all other axes neutral."""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())

    # Yaw minimum
    dut._log.info("Driving yaw low (rotate CCW)")
    await drive_controls(dut, throttle=0.5, pitch=0.5, roll=0.5, yaw=0)
    levels = await read_mixer_values(dut)
    dut._log.info(f"Levels (min): {levels}")

    min_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.info(f"Duties (min): {min_duties}")
    # expect CW motors (2, 4) low, CCW motors (1, 3) high
    assert min_duties[2] == min_duties[4], f"Motors 2 ({min_duties[1]}) and 4 ({min_duties[4]}) not equal"
    assert min_duties[1] == min_duties[3], f"Motors 1 ({min_duties[2]}) and 3 ({min_duties[3]}) not equal"
    assert min_duties[1] >  min_duties[2], f"CW motors ({min_duties[2]}) not slower than CCW motors ({min_duties[1]})"

    # Yaw maximum
    dut._log.info("Driving yaw high (rotate CW)")
    await drive_controls(dut, throttle=0.5, pitch=0.5, roll=0.5, yaw=1)
    levels = await read_mixer_values(dut)
    dut._log.info(f"Levels (min): {levels}")
    max_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.info(f"Duties (max): {max_duties}")
    # expect CW motors (2, 4) high, CCW motors (1, 3) low
    assert max_duties[2] == max_duties[4], f"Motors 2 ({max_duties[1]}) and 4 ({max_duties[4]}) not equal"
    assert max_duties[1] == max_duties[3], f"Motors 1 ({max_duties[2]}) and 3 ({max_duties[3]}) not equal"
    assert max_duties[1] <  max_duties[2], f"CCW motors ({max_duties[1]}) not slower than CW motors ({max_duties[2]})"


@cocotb.test(skip=True)
async def test_control_extremes(dut):
    """Test extreme control inputs and confirm outputs stay within bounds and match expected behavior"""
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())

    dut._log.info("Driving all inputs low")
    await drive_controls(dut, throttle=0, pitch=0, roll=0, yaw=0)
    levels = await read_mixer_values(dut)
    dut._log.info(f"Levels (min): {levels}")

    min_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.info(f"Duties (min): {min_duties}")
    # check outputs in range (1-2ms)
    for motor, duty in min_duties.items():
        assert duty >= 0.05 and duty <= 0.1, f"All low - Motor {motor} duty out of range at {duty}"
    # for all controls low, motors speeds should be M4 < M1 = M2 = M3
    assert min_duties[1] == min_duties[2], f"All low - Motors 1 {min_duties[1]}) and 2 ({min_duties[2]}) not equal"
    assert min_duties[1] == min_duties[3], f"All low - Motors 1 {min_duties[1]}) and 3 ({min_duties[3]}) not equal"
    assert min_duties[4] <  min_duties[1], f"All low - Motor 4 ({min_duties[4]}) not slower than other motors ({min_duties[1]})"


    dut._log.info("Driving all inputs high")
    await drive_controls(dut, throttle=1, pitch=1, roll=1, yaw=1)
    levels = await read_mixer_values(dut)
    dut._log.info(f"Levels (max): {levels}")

    max_duties = await measure_pwm_duty(dut, PERIOD_CYCLES)
    dut._log.info(f"Duties (max): {max_duties}")
    # check outputs in range (1-2ms)
    for motor, duty in max_duties.items():
        assert duty >= 0.05 and duty <= 0.1, f"All high - Motor {motor} duty out of range at {duty}"
    # for all controls low, motors speeds should be M4 > M1 = M2 = M3
    assert max_duties[1] == max_duties[2], f"All high - Motors 1 {max_duties[1]}) and 2 ({max_duties[2]}) not equal"
    assert max_duties[1] == max_duties[3], f"All high - Motors 1 {max_duties[1]}) and 3 ({max_duties[3]}) not equal"
    assert max_duties[4] >  max_duties[1], f"All high - Motor 4 ({max_duties[4]}) not faster than other motors ({max_duties[1]})"
