//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : mixer.v
// Author       : Kyle Minihan
// Created      : 02 October 2025
// Description  : Map the throttle/yaw/pitch/roll (after converting from PWM to int
//                  to the power values for each motor).
//
// Notes: 
//    Motor 1 (Front Left, CCW): Throttle + Pitch + Roll - Yaw
//    Motor 2 (Front Right, CW): Throttle + Pitch - Roll + Yaw
//    Motor 3 (Rear Right, CCW): Throttle - Pitch - Roll - Yaw
//    Motor 4 (Rear Left,   CW): Throttle - Pitch + Roll + Yaw
// 
//////////////////////////////////////////////////////////////////////////////////

module mixer (
    input [7:0] throttle, yaw, pitch, roll,
    output signed [8:0] motor1, motor2, motor3, motor4
);
    wire[7:0] yawSigned, pitchSigned, rollSigned;
    assign yawSigned = $signed(yaw - 128);
    assign pitchSigned = $signed(pitch - 128);
    assign rollSigned = $signed(roll - 128);

    assign motor1 = throttle - pitchSigned + rollSigned - yawSigned;
    assign motor2 = throttle - pitchSigned - rollSigned + yawSigned;
    assign motor3 = throttle + pitchSigned - rollSigned - yawSigned;
    assign motor4 = throttle + pitchSigned + rollSigned + yawSigned;
endmodule
