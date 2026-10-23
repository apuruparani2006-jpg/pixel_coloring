import os
import streamlit as st
from PIL import Image
from colorizer import colorize_image

st.set_page_config(
    page_title="Pixel Colouring AI",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 Pixel Colouring AI")
st.write(
    "Upload a grayscale image to create a colorized version, "
    "or ask the AI assistant about this project."
)

tab_image, tab_assistant, tab_about = st.tabs(
    ["🖼️ Colorize Image", "🤖 AI Assistant", "ℹ️ About"]
)

with tab_image:
    uploaded = st.file_uploader(
        "Choose a grayscale image",
        type=["png", "jpg", "jpeg", "bmp"],
    )

    if uploaded is not None:
        try:
            image = Image.open(uploaded).convert("RGB")
            st.image(image, caption="Uploaded image", use_container_width=True)

            if st.button("🎨 Colorize Image", type="primary"):
                with st.spinner("Colorizing image..."):
                    result = colorize_image(image)

                left, right = st.columns(2)
                with left:
                    st.image(image, caption="Original", use_container_width=True)
                with right:
                    st.image(result, caption="Colorized result", use_container_width=True)

                from io import BytesIO

                output = BytesIO()
                result.save(output, format="PNG")

                st.download_button(
                    "⬇️ Download colorized image",
                    data=output.getvalue(),
                    file_name="colorized_image.png",
                    mime="image/png",
                )
        except Exception as exc:
            st.error("The image could not be processed.")
            st.caption(str(exc))

with tab_assistant:
    st.subheader("Ask the Pixel Colouring AI assistant")
    st.write(
        "Ask about Python, image colorization, Streamlit, "
        "Verilog, testbenches, GitHub, or deployment."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your project")

    if question:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY", "")
            except Exception:
                api_key = ""

        if not api_key:
            st.error(
                "The API key is not configured. Add OPENAI_API_KEY "
                "to your local Streamlit secrets or Render environment."
            )
        else:
            from openai import OpenAI

            st.session_state.chat_history.append(
                {"role": "user", "content": question}
            )

            with st.chat_message("user"):
                st.markdown(question)

            try:
                client = OpenAI(api_key=api_key)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = client.responses.create(
                            model="gpt-4.1-mini",
                            instructions=(
                                "You are a friendly, beginner-level technical "
                                "assistant for a student project called Pixel "
                                "Colouring AI. Explain Python, pretrained image "
                                "colorization, Streamlit, Verilog RGB selection, "
                                "testbenches, GitHub, and deployment clearly. "
                                "The Verilog module is a separate RGB selector; "
                                "it does not perform AI colorization. Never "
                                "claim that you ran code or inspected files "
                                "unless that actually happened."
                            ),
                            input=question,
                        )
                        answer = response.output_text
                        st.markdown(answer)

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as exc:
                st.error(
                    "The AI request failed. Check your API key, API account "
                    "billing/access, model availability, and connection."
                )
                st.caption(str(exc))

    if st.button("Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

with tab_about:
    st.subheader("About this project")
    st.markdown(
        """
- **Python and OpenCV:** process images and run the pretrained model.
- **Streamlit:** provides the web interface.
- **OpenAI API:** answers technical questions about the project.
- **Verilog:** demonstrates selection between grayscale and RGB values.
- **GitHub and Render:** store the code and host the web application.
        """
    )
