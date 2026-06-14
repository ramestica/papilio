`include "prbs.v"

module adc_dac(
    input              CLK,
    output             CLK_ADC,
    output             CLK_ADC_90d,
    output             CLK_DAC,
    input  [N-1:0]     ADC,
    output [N-1:0]     DAC,
    output reg [N-1:0] DIFF
);

parameter N = 8;

wire CLK_INT_ADC, CLK_INT_ADC_90d, CLK_INT_DAC;
wire pll_locked;
wire pll_fb;

PLL_BASE #(
    .BANDWIDTH          ("OPTIMIZED"),
    .CLK_FEEDBACK       ("CLKFBOUT"),
    .COMPENSATION       ("INTERNAL"),
    .DIVCLK_DIVIDE      (1),
    .CLKFBOUT_MULT      (16),
    .CLKFBOUT_PHASE     (0.0),
    .CLKOUT0_DIVIDE     (16),
    .CLKOUT0_PHASE      (0.0),
    .CLKOUT1_DIVIDE     (16),
    .CLKOUT1_PHASE      (0.0),
    .CLKOUT2_DIVIDE     (16),
    .CLKOUT2_PHASE      (90.0),
    .CLKIN_PERIOD       (31.25),
    .REF_JITTER         (0.100)
) pll (
    .CLKFBOUT           (pll_fb),
    .CLKFBIN            (pll_fb),
    .CLKOUT0            (CLK_INT_ADC),
    .CLKOUT1            (CLK_INT_DAC),
    .CLKOUT2            (CLK_INT_ADC_90d),
    .CLKOUT3            (),
    .CLKOUT4            (),
    .CLKOUT5            (),
    .CLKIN              (CLK),
    .LOCKED             (pll_locked),
    .RST                (1'b0)
);

ODDR2 #(.DDR_ALIGNMENT("NONE"), .INIT(1'b0), .SRTYPE("SYNC"))
ODDR_ADC (
    .Q  (CLK_ADC),
    .C0 (CLK_INT_ADC),
    .C1 (~CLK_INT_ADC),
    .CE (1'b1),
    .D0 (1'b1),
    .D1 (1'b0),
    .R  (1'b0),
    .S  (1'b0)
);

ODDR2 #(.DDR_ALIGNMENT("NONE"), .INIT(1'b0), .SRTYPE("SYNC"))
ODDR_ADC_90d (
    .Q  (CLK_ADC_90d),
    .C0 (CLK_INT_ADC_90d),
    .C1 (~CLK_INT_ADC_90d),
    .CE (1'b1),
    .D0 (1'b1),
    .D1 (1'b0),
    .R  (1'b0),
    .S  (1'b0)
);

ODDR2 #(.DDR_ALIGNMENT("NONE"), .INIT(1'b0), .SRTYPE("SYNC"))
ODDR_DAC (
    .Q  (CLK_DAC),
    .C0 (CLK_INT_DAC),
    .C1 (~CLK_INT_DAC),
    .CE (1'b1),
    .D0 (1'b1),
    .D1 (1'b0),
    .R  (1'b0),
    .S  (1'b0)
);

prbs_generate #(.PN(8), .TAP1(5), .TAP2(4), .TAP3(3)) prbs (
    .prbs  (DAC),
    .clk   (CLK_INT_DAC),
    .reset (~pll_locked)
);

always @(negedge CLK_INT_ADC) begin
    DIFF <= ADC;
end

endmodule
