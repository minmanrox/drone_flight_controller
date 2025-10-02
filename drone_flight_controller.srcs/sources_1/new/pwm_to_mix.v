`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : pwm_to_mix.v
// Author       : Kyle Minihan
// Created      : 02 October 2025
// Description  : Convert the input PWM signals from the receiver into signed values
//                  for throttle/pitch/roll/yaw
// 
//////////////////////////////////////////////////////////////////////////////////

`include "system_params.vh"

module pwm_to_mix(
    input clk,          // System clock (e.g., 125 MHz)
    input pwm_in,       // PWM signal from CRSF-PWM
    output reg signed [7:0] value // Normalized output
);
    reg [19:0] high_counter = 0;
    reg [19:0] pulse_width = 0;

    always @(posedge clk) begin
        if (pwm_in)
            high_counter <= high_counter + 1;
        else begin
            pulse_width  <= high_counter;
            high_counter <= 0;
            // Map pulse_width to signed value, e.g. from 1ms-2ms to -127:+127
            value <= $signed((pulse_width - `PWM_PERIOD) * 127 / `PWM_PERIOD); // for 125MHz
        end
    end
endmodule
