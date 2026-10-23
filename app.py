import streamlit as st
from colorizer import colorize_image

# Configure page settings
st.set_page_config(
    page_title="Pixel Colouring AI",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Pixel Colouring AI")
st.write("Upload a black and white image to automatically colorize it using AI!")

# File uploader widget
uploaded_file = st.file_uploader(
    "Choose a black and white image...", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # Get raw image bytes safely
    image_bytes = uploaded_file.getvalue()
    
    # Display the original image
    st.subheader("Original Image")
    st.image(uploaded_file)
    
    # Process image on button click
    if st.button("Colorize Image"):
        with st.spinner("Downloading AI model & colorizing image... Please wait 10-20 seconds..."):
            colorized_np = colorize_image(image_bytes)
            
            # Safely render image only if colorized_np is a valid NumPy array
            if colorized_np is not None:
                # Convert OpenCV BGR format to RGB for Streamlit display
                colorized_rgb = colorized_np[:, :, ::-1]
                
                st.subheader("Colorized Result")
                st.image(colorized_rgb)
                st.success("Image colorized successfully!")
            else:
                st.error("The image could not be processed. Please check the detailed error above or try another image.")
