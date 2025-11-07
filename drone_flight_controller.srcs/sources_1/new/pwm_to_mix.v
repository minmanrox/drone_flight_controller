`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : pwm_to_mix.v
// Author       : Kyle Minihan
// Created      : 02 October 2025
// Description  : Convert the input PWM signals from the receiver into unsigned values
//                  for throttle/pitch/roll/yaw
// 
//////////////////////////////////////////////////////////////////////////////////

`include "system_params.vh"

module pwm_to_mix(
    input clk,          // System clock (e.g., 125 MHz)
    input pwm_in,       // PWM signal from CRSF-PWM
    output reg [7:0] value // Normalized output
);
    reg [19:0] high_counter = 0;
    reg [19:0] pulse_width = 0;
//    reg [19:0] bounded_pw;
    reg prev_pwm_in = 0;

    always @(posedge clk) begin
        prev_pwm_in <= pwm_in; // register for edge detection

        // Count HIGH time
        if (pwm_in)
            high_counter <= high_counter + 1;
        else
            high_counter <= 0;

        // Falling edge detector: previous=1, current=0
        if (prev_pwm_in & ~pwm_in) begin
            // clamp value to range
            if (high_counter <= `PWM_MIN)
                pulse_width <= `PWM_MIN;
            else if (high_counter >= `PWM_MAX)
                pulse_width <= `PWM_MAX;
            else
                pulse_width <= high_counter;
            
//            pulse_width <= high_counter;
            // Map pulse_width to unsigned value
            value <= ((pulse_width - `PWM_MIN) * 255 / (`PWM_MAX-`PWM_MIN));
        end
    end
endmodule
