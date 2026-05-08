`timescale 1 ns / 1 ps

module picorv32_bp_top (
    input clk,
    input resetn,
    
    // Memory interface out
    output        mem_valid,
    output        mem_instr,
    input         mem_ready,
    output [31:0] mem_addr,
    output [31:0] mem_wdata,
    output [ 3:0] mem_wstrb,
    input  [31:0] mem_rdata
);

    // Wires for Neural Branch History Table
    wire bht_predict_taken;
    wire [35:0] trace_data;
    wire        trace_valid;

    // Decode trace data to update BHT (simplified mapping for demonstration)
    // In picorv32, trace_data[35:32] == 1 denotes a TRACE_BRANCH 
    wire is_trace_branch = (trace_data[35:32] == 4'b0001);
    
    // We pass true logic if the trace is valid and identifies a branch.
    // In a real pipeline, the taken flag & mispredict flag would be computed based on predictions,
    // but PicoRV32 operates multi-cycle without speculative branch recovery, so we provide an
    // active feedback loop to let the BHT train alongside the regular fetch execution context.
    wire bht_train_valid = trace_valid && is_trace_branch;
    wire bht_train_taken = 1'b1; // Dummy value: assuming taken if branched.
    wire bht_miss        = 1'b1; // Dummy value: always train BHT on observed branches for demonstration

    // 1. Instantiate the PicoRV32 Core
    // We enable trace to capture the branch instruction events
    picorv32 #(
        .ENABLE_TRACE(1)
    ) cpu (
        .clk        (clk),
        .resetn     (resetn),

        .mem_valid  (mem_valid),
        .mem_instr  (mem_instr),
        .mem_ready  (mem_ready),
        .mem_addr   (mem_addr),
        .mem_wdata  (mem_wdata),
        .mem_wstrb  (mem_wstrb),
        .mem_rdata  (mem_rdata),
        
        .trace_valid(trace_valid),
        .trace_data (trace_data)
    );

    // 2. Instantiate our standalone Neural Branch Predictor
    // We hook its prediction phase to memory fetches (PC addresses)
    neural_bht bht (
        .clk              (clk),
        .reset            (~resetn),
        
        // Let it predict ahead whenever the processor fetches an instruction
        .req_pc           (mem_addr),
        .req_taken        (bht_predict_taken),
        
        // Feed real execution results back to train the neural perceptron weights
        .update_valid     (bht_train_valid),
        .update_pc        ({trace_data[31:1], 1'b0}),
        .update_taken     (bht_train_taken),
        .update_mispredict(bht_miss)
    );

endmodule
