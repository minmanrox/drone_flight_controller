`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : mix_to_pwm_esc.v
// Author       : Kyle Minihan
// Created      : 02 October 2025
// Description  : Convert the output of the mixer module to a PWM signal, sent to
//                  the ESCs.
// 
//////////////////////////////////////////////////////////////////////////////////

`include "system_params.vh"

module mix_to_pwm (
    input clk,                    // 125 MHz
    input signed [8:0] motor_value, // Mixer value (-127 to +127 ideally)
    output reg pwm_out
);
    reg [21:0] counter = 0;

    // Use wire with assign for combinational logic
    wire [19:0] pulse_width;
    assign pulse_width = `PWM_MIN + ((motor_value + 127) * `PWM_MAX-`PWM_MIN / 254);

    always @(posedge clk) begin
        if (counter < `PWM_PERIOD - 1)
            counter <= counter + 1;
        else
            counter <= 0;

        pwm_out <= (counter < pulse_width);
    end

endmodule
