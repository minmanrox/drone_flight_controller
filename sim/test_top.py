# sim/cocotb/test_top.py
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


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
    await Timer(1, units="ns")

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
