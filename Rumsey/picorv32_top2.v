module picorv32_top (
    input wire clk,
    input wire resetn
);

    wire        mem_valid;
    wire        mem_instr;
    reg         mem_ready;
    wire [31:0] mem_addr;
    wire [31:0] mem_wdata;
    wire [3:0]  mem_wstrb;
    wire [31:0] mem_rdata;

    wire [8:0] sram_addr;
    wire       sram_write;

    assign sram_addr  = mem_addr[10:2];
    assign sram_write = |mem_wstrb;

    always @(posedge clk) begin
        if (!resetn)
            mem_ready <= 1'b0;
        else
            mem_ready <= mem_valid;
    end

    picorv32 #(
        .ENABLE_COUNTERS     (0),
        .ENABLE_COUNTERS64   (0),
        .ENABLE_REGS_16_31   (1),
        .ENABLE_REGS_DUALPORT(1),
        .TWO_STAGE_SHIFT     (1),
        .BARREL_SHIFTER      (0),
        .TWO_CYCLE_COMPARE   (0),
        .TWO_CYCLE_ALU       (0),
        .COMPRESSED_ISA      (0),
        .CATCH_MISALIGN      (1),
        .CATCH_ILLINSN       (1),
        .ENABLE_PCPI         (0),
        .ENABLE_MUL          (0),
        .ENABLE_FAST_MUL     (0),
        .ENABLE_DIV          (0),
        .ENABLE_IRQ          (0),
        .ENABLE_IRQ_QREGS    (1),
        .ENABLE_IRQ_TIMER    (1),
        .ENABLE_TRACE        (0),
        .REGS_INIT_ZERO      (0),
        .MASKED_IRQ          (32'h0000_0000),
        .LATCHED_IRQ         (32'hffff_ffff),
        .PROGADDR_RESET      (32'h0000_0000),
        .PROGADDR_IRQ        (32'h0000_0010),
        .STACKADDR           (32'h0000_0800)
    ) cpu (
        .clk        (clk),
        .resetn     (resetn),

        .mem_valid  (mem_valid),
        .mem_instr  (mem_instr),
        .mem_ready  (mem_ready),
        .mem_addr   (mem_addr),
        .mem_wdata  (mem_wdata),
        .mem_wstrb  (mem_wstrb),
        .mem_rdata  (mem_rdata)
    );

    sky130_sram_2kbyte_1rw1r_32x512_8 ram (
        .clk0   (clk),
        .csb0   (!mem_valid),
        .web0   (!sram_write),
        .wmask0 (mem_wstrb),
        .addr0  (sram_addr),
        .din0   (mem_wdata),
        .dout0  (mem_rdata),

        .clk1   (clk),
        .csb1   (1'b1),
        .addr1  (9'b0),
        .dout1  ()
    );

endmodule
