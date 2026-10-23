`timescale 1ns/1ps

module tb_pixel_rgb;

    reg select_color;
    reg [7:0] gray;
    reg [7:0] red_in, green_in, blue_in;

    wire [7:0] red_out, green_out, blue_out;

    pixel_rgb dut (
        .select_color(select_color),
        .gray(gray),
        .red_in(red_in),
        .green_in(green_in),
        .blue_in(blue_in),
        .red_out(red_out),
        .green_out(green_out),
        .blue_out(blue_out)
    );

    initial begin
        $dumpfile("pixel_rgb.vcd");
        $dumpvars(0, tb_pixel_rgb);

        gray = 8'd100;
        red_in = 8'd255;
        green_in = 8'd0;
        blue_in = 8'd0;

        select_color = 1'b0;
        #10;

        if (red_out !== 100 ||
            green_out !== 100 ||
            blue_out !== 100)
            $display("FAIL: grayscale selection");
        else
            $display("PASS: grayscale selection");

        select_color = 1'b1;
        #10;

        if (red_out !== 255 ||
            green_out !== 0 ||
            blue_out !== 0)
            $display("FAIL: RGB selection");
        else
            $display("PASS: RGB selection");

        $finish;
    end

endmodule
