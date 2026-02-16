`timescale 1ns / 1ps

module pwm_generator_tb;
    reg clk;
    reg rst;
    reg [6:0] duty_cycle;
    wire pwm_out;
    
    parameter CLK_PERIOD = 83.333;
    
    pwm_generator uut (
        .clk(clk),
        .rst(rst),
        .duty_cycle(duty_cycle),
        .pwm_out(pwm_out)
    );
    
    initial begin
        clk = 0;
        forever #(CLK_PERIOD/2) clk = ~clk;
    end
    
    initial begin
        $dumpfile("pwm_generator_tb.vcd");
        $dumpvars(0, pwm_generator_tb);
        
        rst = 1;
        duty_cycle = 0;
        #1000;
        
        rst = 0;
        duty_cycle = 25;
        #100000;
        
        duty_cycle = 50;
        #100000;
        
        duty_cycle = 75;
        #100000;
        
        $finish;
    end
endmodule