`timescale 1ns / 1ps

module traffic_light_tb;

    reg clk;
    reg rst;
    reg emergency_ns;
    reg emergency_ew;

    wire [2:0] light_ns;
    wire [2:0] light_ew;

    // Instantiate Traffic Light Controller
    traffic_light dut (
        .clk(clk),
        .rst(rst),
        .emergency_ns(emergency_ns),
        .emergency_ew(emergency_ew),
        .light_ns(light_ns),
        .light_ew(light_ew)
    );

    // Generate Clock (20ns Period -> 50MHz)
    always #10 clk = ~clk;

    initial begin
        $dumpfile("traffic_light_tb.vcd");
        $dumpvars(0, traffic_light_tb);

        $monitor("Time=%0t ns | rst=%b | EM_NS=%b EM_EW=%b | Light_NS=%b Light_EW=%b",
                 $time, rst, emergency_ns, emergency_ew, light_ns, light_ew);

        // Initialize inputs
        clk = 0;
        rst = 1;
        emergency_ns = 0;
        emergency_ew = 0;

        #30 rst = 0; // Release Reset

        // Run normal operations
        #600;

        // Trigger Emergency vehicle override on East-West
        $display("\n---> Triggering East-West Emergency Override <---");
        emergency_ew = 1;
        #100;
        emergency_ew = 0; // Clear emergency override

        // Continue normal operation
        #400;

        $display("\n=== Testbench Completed Successfully ===");
        $finish;
    end

endmodule
