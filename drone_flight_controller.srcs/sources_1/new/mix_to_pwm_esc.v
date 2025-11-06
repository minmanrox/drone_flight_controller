`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : mix_to_pwm_esc.v
// Author       : Kyle Minihan
// Created      : 02 October 2025
// Description  : Convert the output of the mixer module to a PWM signal, sent to
//                  the ESCs.
//                  Also includes logic for calibration sequence of the ESCs, first
//                  holding MIN for `CALIB_HOLD cycles, then holding MAX for
//                  `CALIB_HOLD cycles, and then proceeding to normal operation.
// 
//////////////////////////////////////////////////////////////////////////////////

`include "system_params.vh"

module mix_to_pwm (
    input clk,                    // 125 MHz
    input signed [9:0] motor_value, // Mixer value (-512 to +511 ideally)
    output reg pwm_out
);
    reg [21:0] counter = 0;
    reg [29:0] calibration_counter = 0;  // Counter for calibration timing
    reg [1:0] calibration_state = 0;     // FSM for calibration state 0=MIN, 1=MAX, 2=normal
    
    // Calibration timing constants (for 125 MHz clock)
    localparam CAL_TIME = 30'd`CALIB_HOLD;

    // Use wire with assign for combinational logic
    wire [19:0] pulse_width;
    assign pulse_width = `PWM_MIN + ((motor_value + 512) * (`PWM_MAX-`PWM_MIN) / 1024);
    
    // Pulse MIN or MAX based on calibration state
    wire [19:0] calibration_pulse_width;
    assign calibration_pulse_width = (calibration_state == 2'd0) ? `PWM_MAX : `PWM_MIN;
    
    // Select pulse width based on calibration state
    wire [19:0] active_pulse_width;
    assign active_pulse_width = (calibration_state == 2'd2) ? pulse_width : calibration_pulse_width;
    
    // Calibration state machine
    always @(posedge clk) begin
        if (calibration_state != 2'd2) begin
            if (calibration_counter < CAL_TIME - 1) begin
                calibration_counter <= calibration_counter + 1;
            end else begin
                calibration_counter <= 0;
                calibration_state <= calibration_state + 1;
            end
        end
    end

    // Generate PWM by counting up to pulse_width
    always @(posedge clk) begin
        if (counter < `PWM_PERIOD - 1)
            counter <= counter + 1;
        else
            counter <= 0;

        pwm_out <= (counter < active_pulse_width);
    end

endmodule
