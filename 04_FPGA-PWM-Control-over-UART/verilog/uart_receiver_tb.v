`timescale 1ns / 1ps

module uart_receiver_tb;
    reg clk;
    reg rst;
    reg rx;
    wire [7:0] data;
    wire data_valid;
    
    parameter CLK_PERIOD = 83.333;
    parameter BIT_TIME = 104 * CLK_PERIOD;
    
    uart_receiver uut (
        .clk(clk),
        .rst(rst),
        .rx(rx),
        .data(data),
        .data_valid(data_valid)
    );
    
    initial begin
        clk = 0;
        forever #(CLK_PERIOD/2) clk = ~clk;
    end
    
    initial begin
        $dumpfile("uart_receiver_tb.vcd");
        $dumpvars(0, uart_receiver_tb);
        
        rst = 1;
        rx = 1;
        #1000;
        rst = 0;
        #1000;
        
        rx = 0; #BIT_TIME;
        rx = 1; #BIT_TIME;
        rx = 0; #BIT_TIME;
        rx = 1; #BIT_TIME;
        rx = 0; #BIT_TIME;
        rx = 1; #BIT_TIME;
        rx = 0; #BIT_TIME;
        rx = 1; #BIT_TIME;
        rx = 1; #BIT_TIME;
        
        #(BIT_TIME*10);
        $finish;
    end
endmodule