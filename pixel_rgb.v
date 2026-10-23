module pixel_rgb (
    input wire select_color,
    input wire [7:0] gray,
    input wire [7:0] red_in,
    input wire [7:0] green_in,
    input wire [7:0] blue_in,
    output wire [7:0] red_out,
    output wire [7:0] green_out,
    output wire [7:0] blue_out
);

    assign red_out   = select_color ? red_in   : gray;
    assign green_out = select_color ? green_in : gray;
    assign blue_out  = select_color ? blue_in  : gray;

endmodule
