module uart_receiver (
    input wire clk,
    input wire rst,
    input wire rx,
    output reg [7:0] data,
    output reg data_valid
);
    parameter CLK_PER_BIT = 104;
    
    reg [2:0] state = 0;
    reg [6:0] clk_count = 0;
    reg [2:0] bit_index = 0;
    reg [7:0] rx_buffer;
    
    localparam IDLE = 0;
    localparam START = 1;
    localparam DATA = 2;
    localparam STOP = 3;
    
    always @(posedge clk) begin
        if (rst) begin
            state <= IDLE;
            data_valid <= 0;
            clk_count <= 0;
            bit_index <= 0;
        end else begin
            case (state)
                IDLE: begin
                    data_valid <= 0;
                    clk_count <= 0;
                    bit_index <= 0;
                    if (rx == 0) state <= START;
                end
                
                START: begin
                    if (clk_count == (CLK_PER_BIT-1)/2) begin
                        if (rx == 0) begin
                            clk_count <= 0;
                            state <= DATA;
                        end else begin
                            state <= IDLE;
                        end
                    end else begin
                        clk_count <= clk_count + 1;
                    end
                end
                
                DATA: begin
                    if (clk_count == CLK_PER_BIT-1) begin
                        clk_count <= 0;
                        rx_buffer[bit_index] <= rx;
                        if (bit_index == 7) begin
                            state <= STOP;
                        end else begin
                            bit_index <= bit_index + 1;
                        end
                    end else begin
                        clk_count <= clk_count + 1;
                    end
                end
                
                STOP: begin
                    if (clk_count == CLK_PER_BIT-1) begin
                        data <= rx_buffer;
                        data_valid <= 1;
                        state <= IDLE;
                    end else begin
                        clk_count <= clk_count + 1;
                    end
                end
            endcase
        end
    end
endmodule