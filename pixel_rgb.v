// 16-to-1 Multiplexer / LUT Style 7-Segment Display Decoder
module segment_decoder (
    input  wire [3:0] bcd,   // 4-bit input select line (0-15 / 0-F)
    output reg  [6:0] seg   // 7-segment output bus [a, b, c, d, e, f, g]
);

    // Look-Up Table (LUT) storing 7-segment active-low output patterns
    // 0 = Segment ON, 1 = Segment OFF
    wire [6:0] pattern [0:15];

    assign pattern[0]  = 7'b0000001; // Digit 0
    assign pattern[1]  = 7'b1001111; // Digit 1
    assign pattern[2]  = 7'b0010010; // Digit 2
    assign pattern[3]  = 7'b0000110; // Digit 3
    assign pattern[4]  = 7'b1001100; // Digit 4
    assign pattern[5]  = 7'b0100100; // Digit 5
    assign pattern[6]  = 7'b0100000; // Digit 6
    assign pattern[7]  = 7'b0001101; // Digit 7
    assign pattern[8]  = 7'b0000000; // Digit 8
    assign pattern[9]  = 7'b0000100; // Digit 9
    assign pattern[10] = 7'b0001000; // Digit A
    assign pattern[11] = 7'b1100000; // Digit b
    assign pattern[12] = 7'b0110001; // Digit C
    assign pattern[13] = 7'b1000010; // Digit d
    assign pattern[14] = 7'b0110000; // Digit E
    assign pattern[15] = 7'b0111000; // Digit F

    // MUX Routing Logic
    always @(*) begin
        seg = pattern[bcd]; // Output selected by 4-bit bcd input
    end

endmodule
