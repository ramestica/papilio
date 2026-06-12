module blinky (
    input  clk,
    output led
);
    reg [24:0] counter = 0;

    always @(posedge clk) begin
        counter <= counter + 1;
    end

    assign led = counter[24];
endmodule
