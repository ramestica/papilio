module prbs_generate
  (// outputs
   prbs,
   // inputs
   clk,
   reset);

   parameter
     PN   = 8,
     TAP1 = 5,
     TAP2 = 4,
     TAP3 = 3;

   output reg [PN-1:0] prbs;
   input               clk, reset;

   reg [PN-1:0] prbs_state;

   always @(posedge clk) begin
      if (reset)
        prbs_state <= 1;
      else
        prbs_state <= {prbs_state[PN-2:0], prbs_state[PN-1] ^ prbs_state[TAP1] ^ prbs_state[TAP2] ^ prbs_state[TAP3]};
      prbs <= prbs_state;
   end

endmodule
