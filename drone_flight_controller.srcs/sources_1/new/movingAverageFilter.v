`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : top_module.v
// Author       : Kyle Minihan
// Created      : 02 November 2025
// Description  : Moving-average filter to smooth output.
// 
//////////////////////////////////////////////////////////////////////////////////
//`define N   5

module movingAverageFilter #(
    parameter N = 5
)(
    input clk,
    input [9:0] unfiltered,
    output reg [9:0] filtered
    );
    
    reg [13:0] sum;
    reg [9:0] data [0:N-1];
    integer i;
    
    always @(posedge clk) begin
      sum <= sum + unfiltered - data[N-1];
      // shift register logic for data[]
      for (i = N-1; i > 0; i = i - 1)
        data[i] <= data[i-1];
      data[0] <= unfiltered;
    
      filtered <=  sum / N;
    end

endmodule
