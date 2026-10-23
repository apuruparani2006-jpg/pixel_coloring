import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Streamlit Page Setup
st.set_page_config(page_title="Seven Segment Verilog Simulator", page_icon="💡", layout="wide")

st.title("💡 Seven-Segment Display Verilog Visualizer")
st.write("Simulate and verify 4-bit Binary to 7-Segment HDL multiplexer logic in real time!")

col1, col2 = st.columns([1, 1])

# Look-Up Table mapping (0 = ON, 1 = OFF for Active-Low)
segment_lut = {
    0: "0000001", 1: "1001111", 2: "0010010", 3: "0000110",
    4: "1001100", 5: "0100100", 6: "0100000", 7: "0001101",
    8: "0000000", 9: "0000100", 10: "0001000", 11: "1100000",
    12: "0110001", 13: "1000010", 14: "0110000", 15: "0111000"
}

with col1:
    st.subheader("1. Digital Input Controls")
    input_val = st.slider("Select Hex/Decimal Value (0-15):", min_value=0, max_value=15, value=5)
    
    # 4-bit Binary formatting
    binary_str = format(input_val, '04b')
    st.info(f"**Binary MUX Select Line (`bcd`):** `4'b{binary_str}` | **Hex:** `4'h{input_val:X}`")

    # MUX evaluation
    seg_bits = segment_lut[input_val]
    signals = {seg: int(bit) == 0 for seg, bit in zip(['a', 'b', 'c', 'd', 'e', 'f', 'g'], seg_bits)}

    st.subheader("2. Simulated Signal Outputs")
    st.json({f"Segment {k}": "HIGH (ON)" if v else "LOW (OFF)" for k, v in signals.items()})

with col2:
    st.subheader("3. Rendered Hardware Display")
    
    # Render LED Segments using Matplotlib
    fig, ax = plt.subplots(figsize=(4, 6))
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 4.5)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('#0e1117')

    color_on = "#00FF66"   # Bright Green LED
    color_off = "#1e2530"  # Dark unlit segment

    # 7-Segment Polygon Geometry
    segments = {
        'a': [[0.2, 3.8], [1.8, 3.8], [1.6, 3.5], [0.4, 3.5]],
        'b': [[1.85, 3.7], [1.85, 2.1], [1.55, 2.25], [1.55, 3.4]],
        'c': [[1.85, 1.9], [1.85, 0.3], [1.55, 0.6], [1.55, 1.75]],
        'd': [[0.2, 0.2], [1.8, 0.2], [1.6, 0.5], [0.4, 0.5]],
        'e': [[0.15, 0.3], [0.15, 1.9], [0.45, 1.75], [0.45, 0.6]],
        'f': [[0.15, 2.1], [0.15, 3.7], [0.45, 3.4], [0.45, 2.25]],
        'g': [[0.2, 2.0], [1.8, 2.0], [1.6, 2.15], [0.4, 2.15], [0.4, 1.85], [1.6, 1.85]]
    }

    # Draw each active/inactive segment
    for name, poly in segments.items():
        is_lit = signals[name]
        c = color_on if is_lit else color_off
        polygon = patches.Polygon(poly, closed=True, facecolor=c, edgecolor='#0e1117', linewidth=2)
        ax.add_patch(polygon)

    st.pyplot(fig)

st.markdown("---")
st.subheader("4. Generated Verilog Module (`decoder.v`)")

with st.expander("Click to view corresponding Verilog module"):
    st.code("""
module segment_decoder (
    input  wire [3:0] bcd,   // 4-bit select line
    output reg  [6:0] seg   // 7-segment output
);
    wire [6:0] pattern [0:15];

    assign pattern[0]  = 7'b0000001; // 0
    assign pattern[1]  = 7'b1001111; // 1
    assign pattern[2]  = 7'b0010010; // 2
    assign pattern[3]  = 7'b0000110; // 3
    assign pattern[4]  = 7'b1001100; // 4
    assign pattern[5]  = 7'b0100100; // 5
    assign pattern[6]  = 7'b0100000; // 6
    assign pattern[7]  = 7'b0001101; // 7
    assign pattern[8]  = 7'b0000000; // 8
    assign pattern[9]  = 7'b0000100; // 9
    assign pattern[10] = 7'b0001000; // A
    assign pattern[11] = 7'b1100000; // b
    assign pattern[12] = 7'b0110001; // C
    assign pattern[13] = 7'b1000010; // d
    assign pattern[14] = 7'b0110000; // E
    assign pattern[15] = 7'b0111000; // F

    always @(*) begin
        seg = pattern[bcd];
    end
endmodule
""", language="verilog")
