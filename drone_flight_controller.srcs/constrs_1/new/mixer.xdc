#################################################################################
# 
# Project      : Drone Flight Controller
# File         : mixer.xdc
# Author       : Kyle Minihan
# Created      : 19 October 2025
# Description  : Constraints to map mixer to FPGA
# 
################################################################################

# TODO: describe pin mappings

# Clock input (typical Zybo Z7-10 125MHz oscillator)
set_property PACKAGE_PIN K17 [get_ports {clk}]
set_property IOSTANDARD LVCMOS33 [get_ports {clk}]
create_clock -period 8.00 -name clk -waveform {0 4} [get_ports {clk}]

# PWM inputs
set_property PACKAGE_PIN V15 [get_ports {pwm_in1}]
set_property IOSTANDARD LVCMOS33 [get_ports {pwm_in1}]

set_property PACKAGE_PIN T11 [get_ports {pwm_in2}]
set_property IOSTANDARD LVCMOS33 [get_ports {pwm_in2}]

set_property PACKAGE_PIN W14 [get_ports {pwm_in3}]
set_property IOSTANDARD LVCMOS33 [get_ports {pwm_in3}]

set_property PACKAGE_PIN T12 [get_ports {pwm_in4}]
set_property IOSTANDARD LVCMOS33 [get_ports {pwm_in4}]

set_property PACKAGE_PIN V12 [get_ports {arm_in}]
set_property IOSTANDARD LVCMOS33 [get_ports {arm_in}]

# PWM outputs
set_property PACKAGE_PIN T14 [get_ports {pwm_out1}]
set_property IOSTANDARD LVCMOS33 [get_ports {pwm_out1}]

set_property PACKAGE_PIN P14 [get_ports {pwm_out2}]
set_property IOSTANDARD LVCMOS33 [get_ports {pwm_out2}]

set_property PACKAGE_PIN U14 [get_ports {pwm_out3}]
set_property IOSTANDARD LVCMOS33 [get_ports {pwm_out3}]

set_property PACKAGE_PIN V17 [get_ports {pwm_out4}]
set_property IOSTANDARD LVCMOS33 [get_ports {pwm_out4}]

# Buttons/LEDs
set_property PACKAGE_PIN K18 [get_ports {calib_reset_button}]
set_property IOSTANDARD LVCMOS33 [get_ports {calib_reset_button}]

set_property PACKAGE_PIN M14 [get_ports {calibration_led}]
set_property IOSTANDARD LVCMOS33 [get_ports {calibration_led}]
