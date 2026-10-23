// Traffic Light Controller FSM with Emergency Overrides
module traffic_light (
    input  wire       clk,           // System Clock
    input  wire       rst,           // Active-HIGH Reset
    input  wire       emergency_ns,  // Emergency Override for North-South
    input  wire       emergency_ew,  // Emergency Override for East-West
    output reg  [2:0] light_ns,      // North-South Lights [Red, Yellow, Green]
    output reg  [2:0] light_ew       // East-West Lights   [Red, Yellow, Green]
);

    // Light encoding definitions: [RED, YELLOW, GREEN]
    localparam RED    = 3'b100;
    localparam YELLOW = 3'b010;
    localparam GREEN  = 3'b001;

    // FSM State Encoding
    localparam S_NS_GREEN  = 2'b00;
    localparam S_NS_YELLOW = 2'b01;
    localparam S_EW_GREEN  = 2'b10;
    localparam S_EW_YELLOW = 2'b11;

    reg [1:0] state, next_state;
    reg [3:0] timer;

    // 1. Synchronous State & Timer Register
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= S_NS_GREEN;
            timer <= 4'd0;
        end else begin
            if (emergency_ns || emergency_ew) begin
                timer <= 4'd0; // Reset internal timer during overrides
            end else if (state != next_state) begin
                state <= next_state;
                timer <= 4'd0; // Reset timer on state transition
            end else begin
                timer <= timer + 1'b1;
            end
        end
    end

    // 2. Next State Combinational Logic
    always @(*) begin
        case (state)
            S_NS_GREEN: begin
                if (timer >= 4'd9) next_state = S_NS_YELLOW; // 10 cycles green
                else               next_state = S_NS_GREEN;
            end
            
            S_NS_YELLOW: begin
                if (timer >= 4'd2) next_state = S_EW_GREEN;  // 3 cycles yellow
                else               next_state = S_NS_YELLOW;
            end
            
            S_EW_GREEN: begin
                if (timer >= 4'd9) next_state = S_EW_YELLOW; // 10 cycles green
                else               next_state = S_EW_GREEN;
            end
            
            S_EW_YELLOW: begin
                if (timer >= 4'd2) next_state = S_NS_GREEN;  // 3 cycles yellow
                else               next_state = S_EW_YELLOW;
            end
            
            default: next_state = S_NS_GREEN;
        endcase
    end

    // 3. Output Logic with Emergency Overrides
    always @(*) begin
        if (emergency_ns) begin
            light_ns = GREEN;
            light_ew = RED;
        end else if (emergency_ew) begin
            light_ns = RED;
            light_ew = GREEN;
        end else begin
            case (state)
                S_NS_GREEN:  begin light_ns = GREEN;  light_ew = RED;    end
                S_NS_YELLOW: begin light_ns = YELLOW; light_ew = RED;    end
                S_EW_GREEN:  begin light_ns = RED;    light_ew = GREEN;  end
                S_EW_YELLOW: begin light_ns = RED;    light_ew = YELLOW; end
                default:     begin light_ns = RED;    light_ew = RED;    end
            endcase
        end
    end

endmodule
