`timescale 1us / 1ns
//////////////////////////////////////////////////////////////////////////////////
//
// Project      : Drone Flight Controller
// File         : top_module.v
// Author       : Kyle Minihan
// Created      : 02 October 2025
// Description  : Testbench for top-level quadcopter motor control module
// 
//////////////////////////////////////////////////////////////////////////////////

module top_tb();

    // Inputs for your top-level DUT
    reg clk;
    reg pwm_in1, pwm_in2, pwm_in3, pwm_in4;

    // Outputs from your DUT
    wire pwm_out1, pwm_out2, pwm_out3, pwm_out4;

    // Instantiate the DUT (Design Under Test)
    top_module dut (
        .clk(clk),
        .pwm_in1(pwm_in1),
        .pwm_in2(pwm_in2),
        .pwm_in3(pwm_in3),
        .pwm_in4(pwm_in4),
        .pwm_out1(pwm_out1),
        .pwm_out2(pwm_out2),
        .pwm_out3(pwm_out3),
        .pwm_out4(pwm_out4)
    );

    // Clock Generation (125MHz simulated; period = 8ns)
    initial clk = 0;
    always #0.004 clk = ~clk; // 0.008us = 8ns (for 125MHz)


    // Stimulus: Send various PWM patterns to each channel
    initial begin
        // Initialize all signals
        pwm_in1 = 0; pwm_in2 = 0; pwm_in3 = 0; pwm_in4 = 0;

        // Wait a few cycles for init
        #10;
        $display("Beginning test");

        // Basic test
//        repeat (10) begin
//            // Channel 1: 1ms pulse, Channel 2: 2ms, Channel 3: 1.5ms, Channel 4: 1.75ms
////            $display("Loop");
///*
//    pwm_in1 throttle
//    pwm_in2 yaw
//    pwm_in3 pitch 
//    pwm_in4 roll
//*/  
//            pwm_in1 = 1; pwm_in2 = 1; pwm_in3 = 1; pwm_in4 = 1;
//            #1000;
//            pwm_in1 = 0;            // pwm_in1 goes LOW
////            #1000;
//            #500;
//            pwm_in2 = 0;            // pwm_in2 goes LOW (after 1.5ms total)
//            #250;
//            pwm_in3 = 0;            // pwm_in3 goes LOW (after 1.75ms total)
//            #250;
//            pwm_in4 = 0;            // pwm_in4 goes LOW (after 2ms total)
//            #18000;                 // Finish 20ms period

            
            
//        end
        
        /* Straight flight */
//         All at 0
//        pwm_in1 = 1; pwm_in2 = 1; pwm_in3 = 1; pwm_in4 = 1;
//        #1000;
//        pwm_in1 = 0; pwm_in2 = 1; pwm_in3 = 1; pwm_in4 = 1;
//        #500; 
//        pwm_in1 = 0; pwm_in2 = 0; pwm_in3 = 0; pwm_in4 = 0;
//        #18500;
        
//        // Throttle up
//        pwm_in1 = 1; pwm_in2 = 1; pwm_in3 = 1; pwm_in4 = 1;
//        #1250;
//        pwm_in1 = 0; pwm_in2 = 1; pwm_in3 = 1; pwm_in4 = 1;
//        #250;
//        pwm_in1 = 0; pwm_in2 = 0; pwm_in3 = 0; pwm_in4 = 0;
//        #18500;
        
//        pwm_in1 = 1; pwm_in2 = 1; pwm_in3 = 1; pwm_in4 = 1;
//        #1500;
//        pwm_in1 = 0; pwm_in2 = 0; pwm_in3 = 0; pwm_in4 = 0;
//        #18500;
        
//        pwm_in1 = 1; pwm_in2 = 1; pwm_in3 = 1; pwm_in4 = 1;
//        #1500;
//        pwm_in1 = 1; pwm_in2 = 0; pwm_in3 = 0; pwm_in4 = 0;
//        #500;
//        pwm_in1 = 0; pwm_in2 = 0; pwm_in3 = 0; pwm_in4 = 0;
//        #18000;

        /* Test pitch */
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #1000; pwm_in3 = 0; // pitch back - should see front motors (1&2) greater than rear (3&4)
//        pwm_in4 = 1; #1510; pwm_in4 = 0;
//        #14470;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #1510; pwm_in3 = 0; // pitch nneutral - should see motors equal
//        pwm_in4 = 1; #1510; pwm_in4 = 0;
//        #13960;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #1750; pwm_in3 = 0; // pitch forwards - should see rear motors (3&4) greater than front (1&2)
//        pwm_in4 = 1; #1510; pwm_in4 = 0;
//        #13720;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #2000; pwm_in3 = 0; // pitch forwards - should see rear motors (3&4) greater than front (1&2)
//        pwm_in4 = 1; #1510; pwm_in4 = 0;
//        #13470;

        /* Test yaw */
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1000; pwm_in2 = 0; // yaw left - should see CCW motors (1&3) greater than CW (2&4)
//        pwm_in3 = 1; #1510; pwm_in3 = 0; 
//        pwm_in4 = 1; #1510; pwm_in4 = 0;
//        #14470;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0; // yaw neutral - should see motors equal
//        pwm_in3 = 1; #1510; pwm_in3 = 0;
//        pwm_in4 = 1; #1510; pwm_in4 = 0;
//        #13960;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1750; pwm_in2 = 0; // yaw right - should see CW motors (2&4) greater than CCW (1&3)
//        pwm_in3 = 1; #1510; pwm_in3 = 0;
//        pwm_in4 = 1; #1510; pwm_in4 = 0;
//        #13720;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #2000; pwm_in3 = 0; // yaw right - should see CW motors (2&4) greater than CCW (1&3)
//        pwm_in4 = 1; #1510; pwm_in4 = 0;
//        #13470;
         
         
        /* Test roll */
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #1510; pwm_in3 = 0; 
//        pwm_in4 = 1; #1000; pwm_in4 = 0; // roll left - should see right motors (2&3) greater than left (1&4)
//        #14470;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #1510; pwm_in3 = 0;
//        pwm_in4 = 1; #1510; pwm_in4 = 0; // roll neutral - should see motors equal
//        #13960;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #1510; pwm_in3 = 0;
//        pwm_in4 = 1; #1750; pwm_in4 = 0; // roll right - should see left motors (1&4) greater than right (2&3)
//        #13720;
        
//        pwm_in1 = 1; #1510; pwm_in1 = 0;
//        pwm_in2 = 1; #1510; pwm_in2 = 0;
//        pwm_in3 = 1; #1510; pwm_in3 = 0;
//        pwm_in4 = 1; #2000; pwm_in4 = 0; // roll right - should see left motors (1&4) greater than right (2&3)
//        #13470;

        /* Throttle overflow */
        pwm_in1 = 1; #1000; pwm_in1 = 0; // throttle down - should see low output
        pwm_in2 = 1; #1510; pwm_in2 = 0;
        pwm_in3 = 1; #1510; pwm_in3 = 0; 
        pwm_in4 = 1; #1510; pwm_in4 = 0;
        #14470;
        
        pwm_in1 = 1; #1490; pwm_in1 = 0; // throttle neutral - should see medium output
        pwm_in2 = 1; #1510; pwm_in2 = 0;
        pwm_in3 = 1; #1510; pwm_in3 = 0;
        pwm_in4 = 1; #1510; pwm_in4 = 0;
        #13980;

        
        pwm_in1 = 1; #1510; pwm_in1 = 0; // throttle neutral - should see medium output
        pwm_in2 = 1; #1510; pwm_in2 = 0;
        pwm_in3 = 1; #1510; pwm_in3 = 0;
        pwm_in4 = 1; #1510; pwm_in4 = 0;
        #13960;
        
        pwm_in1 = 1; #1750; pwm_in1 = 0; // throttle up - should see higher output
        pwm_in2 = 1; #1510; pwm_in2 = 0;
        pwm_in3 = 1; #1510; pwm_in3 = 0;
        pwm_in4 = 1; #1510; pwm_in4 = 0;
        #13720;
        
        pwm_in1 = 1; #2000; pwm_in1 = 0; // throttle max - should see highest output
        pwm_in2 = 1; #1510; pwm_in2 = 0;
        pwm_in3 = 1; #1510; pwm_in3 = 0;
        pwm_in4 = 1; #1510; pwm_in4 = 0;
        #13470;

        

        
        // End simulation after pattern
        #200000;
        $display("Test complete");
        $finish;
    end

    // Monitor outputs
//    initial begin
//        $monitor("At time %0t: pwm_out1=%b pwm_out2=%b pwm_out3=%b pwm_out4=%b", $time, pwm_out1, pwm_out2, pwm_out3, pwm_out4);
//    end

endmodule

/*
    // Task to generate a single PWM pulse (default 1.5ms width, 20ms period)
    task send_pwm;
        inout reg pwm_sig;
        input integer width_us;
        begin
            $display("Generating PWM");
            pwm_sig = 1;
            #(width_us);
            pwm_sig = 0;
            #(20000 - width_us); // Complete 20 ms cycle
        end
    endtask
    
                send_pwm(pwm_in1, 1500); // 1.5ms pulse
            send_pwm(pwm_in2, 1500);
            send_pwm(pwm_in3, 1500);
            send_pwm(pwm_in4, 1500);

            send_pwm(pwm_in1, 1000); // 1ms pulse
            send_pwm(pwm_in2, 2000); // 2ms pulse
            send_pwm(pwm_in3, 1000);
            send_pwm(pwm_in4, 2000);
*/
