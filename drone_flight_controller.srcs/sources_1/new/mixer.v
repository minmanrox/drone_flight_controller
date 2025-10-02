//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : mixer.v
// Author       : Kyle Minihan
// Created      : 02 October 2025
// Description  : Map the throttle/yaw/pitch/roll (after converting from PWM to int
//                  to the power values for each motor.
// 
//////////////////////////////////////////////////////////////////////////////////

module mixer (
    input signed [7:0] throttle, yaw, pitch, roll,
    output signed [8:0] motor1, motor2, motor3, motor4
);
    assign motor1 = throttle + pitch + roll - yaw;
    assign motor2 = throttle + pitch - roll + yaw;
    assign motor3 = throttle - pitch - roll - yaw;
    assign motor4 = throttle - pitch + roll + yaw;
endmodule
