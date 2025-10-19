`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : top_module.v
// Author       : Kyle Minihan
// Created      : 02 October 2025
// Description  : Top-level module to combine submodules for the drone flight 
//                  controller.
// 
//////////////////////////////////////////////////////////////////////////////////

`include "system_params.vh"

module top_module (
    input clk,
    input pwm_in1, pwm_in2, pwm_in3, pwm_in4,
    output pwm_out1, pwm_out2, pwm_out3, pwm_out4
);
    wire signed [7:0] throttle, yaw, pitch, roll;
    wire signed [9:0] m1, m2, m3, m4;

    pwm_to_mix r1 (.clk(clk), .pwm_in(pwm_in1), .value(throttle));
    pwm_to_mix r2 (.clk(clk), .pwm_in(pwm_in2), .value(yaw));
    pwm_to_mix r3 (.clk(clk), .pwm_in(pwm_in3), .value(pitch));
    pwm_to_mix r4 (.clk(clk), .pwm_in(pwm_in4), .value(roll));

    mixer mx (.throttle(throttle), .yaw(yaw), .pitch(pitch), .roll(roll),
              .motor1(m1), .motor2(m2), .motor3(m3), .motor4(m4));

    mix_to_pwm e1 (.clk(clk), .motor_value(m1), .pwm_out(pwm_out1));
    mix_to_pwm e2 (.clk(clk), .motor_value(m2), .pwm_out(pwm_out2));
    mix_to_pwm e3 (.clk(clk), .motor_value(m3), .pwm_out(pwm_out3));
    mix_to_pwm e4 (.clk(clk), .motor_value(m4), .pwm_out(pwm_out4));
endmodule
