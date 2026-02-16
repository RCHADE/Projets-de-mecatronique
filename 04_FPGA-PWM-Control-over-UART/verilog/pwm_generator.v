module pwm_generator (
    input wire clk,
    input wire rst,
    input wire [6:0] duty_cycle,
    output reg pwm_out
);
    parameter COUNTER_MAX = 100;
    
    reg [6:0] counter = 0;
    
    always @(posedge clk) begin
        if (rst) begin
            counter <= 0;
            pwm_out <= 0;
        end else begin
            if (counter == COUNTER_MAX-1) begin
                counter <= 0;
            end else begin
                counter <= counter + 1;
            end
            
            if (counter < duty_cycle) begin
                pwm_out <= 1;
            end else begin
                pwm_out <= 0;
            end
        end
    end
endmodule