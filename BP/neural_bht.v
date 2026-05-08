`timescale 1ns / 1ps

module neural_bht (
    input clk,
    input reset,
    
    // Request port
    input [31:0] req_pc,
    output req_taken,
    
    // Update port
    input update_valid,
    input [31:0] update_pc,
    input update_taken,
    input update_mispredict  // 1 if we mispredicted
);

    // BHT parameters
    localparam HIST_LEN = 3;
    localparam WEIGHT_BITS = 8;
    localparam NUM_ENTRIES = 512;
    
    // PC hashing (simplified)
    function [8:0] hashAddr;
        input [31:0] pc;
        begin
            hashAddr = pc[10:2] ^ pc[19:11];
        end
    endfunction

    // Global History Register
    reg [HIST_LEN-1:0] history;
    
    // Wires for SRAM wrapper
    wire [8:0] read_addr = hashAddr(req_pc);
    wire [31:0] read_weights;
    
    wire [8:0] update_addr = hashAddr(update_pc);
    reg [31:0] write_weights;
    reg write_en;
    
    // Instantiate 2kbyte SRAM macro as the Perceptron table
    sky130_sram_2kbyte_1rw1r_32x512_8 table_sram (
        // Port 0: RW (used for updates)
        .clk0(clk),
        .csb0(~write_en), 
        .web0(~write_en),
        .wmask0(4'hf),
        .addr0(update_addr),
        .din0(write_weights),
        .dout0(),
        
        // Port 1: R (used for reads)
        .clk1(clk),
        .csb1(1'b0), // always read
        .addr1(read_addr),
        .dout1(read_weights)
    );

    // Prediction Logic (combinational based on SRAM dout)
    wire signed [7:0] w_bias = read_weights[7:0];
    wire signed [7:0] w_h0 = read_weights[15:8];
    wire signed [7:0] w_h1 = read_weights[23:16];
    wire signed [7:0] w_h2 = read_weights[31:24];

    wire signed [7:0] x_h0 = history[0] ? 8'sd1 : -8'sd1;
    wire signed [7:0] x_h1 = history[1] ? 8'sd1 : -8'sd1;
    wire signed [7:0] x_h2 = history[2] ? 8'sd1 : -8'sd1;
    
    wire signed [15:0] sum = w_bias + (w_h0 * x_h0) + (w_h1 * x_h1) + (w_h2 * x_h2);
    assign req_taken = (sum >= 0);

    // Update Logic
    // Read the current weights to update
    wire signed [7:0] up_w_bias = read_weights[7:0];
    wire signed [7:0] up_w_h0 = read_weights[15:8];
    wire signed [7:0] up_w_h1 = read_weights[23:16];
    wire signed [7:0] up_w_h2 = read_weights[31:24];

    wire signed [7:0] t_val = update_taken ? 8'sd1 : -8'sd1;

    // Helper to saturate add 
    function signed [7:0] sat_add;
        input signed [7:0] a;
        input signed [7:0] b;
        reg signed [8:0] temp;
        begin
            temp = a + b;
            if (temp > 127) sat_add = 8'sd127;
            else if (temp < -128) sat_add = -8'sd128;
            else sat_add = temp[7:0];
        end
    endfunction

    always @(posedge clk) begin
        if (reset) begin
            history <= 0;
            write_en <= 0;
        end else begin
            write_en <= 0; // Default pulse
            if (update_valid) begin
                // Only update weights if mispredicted (simplified)
                if (update_mispredict) begin
                    write_weights[7:0]   <= sat_add(up_w_bias, t_val);
                    write_weights[15:8]  <= sat_add(up_w_h0, t_val * x_h0);
                    write_weights[23:16] <= sat_add(up_w_h1, t_val * x_h1);
                    write_weights[31:24] <= sat_add(up_w_h2, t_val * x_h2);
                    write_en <= 1;
                end
                // Advance history 
                history <= {history[HIST_LEN-2:0], update_taken};
            end
        end
    end

endmodule
