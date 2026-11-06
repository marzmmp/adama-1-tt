/*
 * ADAMA-1 plasticity core for Tiny Tapeout (ttsky26d)
 * Copyright (c) 2026 Major Brinson / TrueSite Technologies
 * SPDX-License-Identifier: Apache-2.0
 *
 * A synapse that strengthens itself in silicon: the silent LTP/LTD update engine and the
 * circadian tick generator from the ADAMA-1 neuromorphic core.
 *
 * Host interface (byte wide, no extra pins):
 *   ui_in[7]   wr_en    write uio_in into the register selected by addr
 *   ui_in[6]   rst_w    synchronous reset of the weight and op registers
 *   ui_in[3:0] addr     0..3 weight byte lane, 4 op, 5 status
 *   uio_in     data
 *   uo_out     readback byte for addr
 *   uio_out[7:4] {satur, floored, tick, wrapped}
 *   uio_oe     8'hF0
 */
module tt_um_marzmmp_adama_plasticity (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);
    wire       rst   = ~rst_n;
    wire       wr_en = ui_in[7] & ena;
    wire       rst_w = ui_in[6];
    wire [3:0] addr  = ui_in[3:0];
    wire [7:0] data  = uio_in;

    reg [31:0] w_in_reg;
    reg [1:0]  op_reg;

    always @(posedge clk) begin
        if (rst || rst_w) begin
            w_in_reg <= 32'd0;
            op_reg   <= 2'd0;
        end else if (wr_en) begin
            case (addr)
                4'd0: w_in_reg[7:0]   <= data;
                4'd1: w_in_reg[15:8]  <= data;
                4'd2: w_in_reg[23:16] <= data;
                4'd3: w_in_reg[31:24] <= data;
                4'd4: op_reg          <= data[1:0];
                default: ;
            endcase
        end
    end

    wire [31:0] w_out;
    wire        satur, floored, tick, wrapped;

    nmf_synapse_update u_upd (
        .op      (op_reg),
        .w_in    (w_in_reg),
        .w_out   (w_out),
        .satur   (satur),
        .floored (floored)
    );

    nmf_tick u_tick (
        .clk        (clk),
        .rst        (rst),
        .preload_en (1'b0),
        .preload    (48'd0),
        .tick       (tick),
        .count      (),
        .wrapped    (wrapped)
    );

    reg [7:0] rd_mux;
    always @(*) begin
        case (addr)
            4'd0: rd_mux = w_out[7:0];
            4'd1: rd_mux = w_out[15:8];
            4'd2: rd_mux = w_out[23:16];
            4'd3: rd_mux = w_out[31:24];
            4'd4: rd_mux = {6'b0, op_reg};
            4'd5: rd_mux = {4'b0, satur, floored, tick, wrapped};
            default: rd_mux = 8'b0;
        endcase
    end

    assign uo_out  = rd_mux;
    assign uio_out = {satur, floored, tick, wrapped, 4'b0};
    assign uio_oe  = 8'hF0;
endmodule
