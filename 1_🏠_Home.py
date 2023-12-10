import streamlit as st
import json
import requests
from streamlit_lottie import st_lottie

st.session_state["response"] = "Incomplete"

st.set_page_config(page_title="MeetingGPT :spiral_note_pad:", page_icon=":spiral_note_pad:", layout="wide")

# Set the font size for the markdown text
markdown_style = """
    <style>
        .custom-font-size {
            font-size: 26px;  /* Replace with your desired font size */
        }
    </style>
"""

# Display markdown text with the specified style
st.markdown(markdown_style, unsafe_allow_html=True)

st.title(":blue[MeetingGPT] 📋📈📊")
st.markdown("### _UCB MIDS Capstone Team: Siva Chamiraju, Francis Lee, Chase Madson, Michael Townsend_")

col1, col2 = st.columns(2)

with col1:

    st.markdown("""<p class='custom-font-size'> <br><br> MeetingGPT is committed to enhancing the efficiency and effectiveness of virtual meetings. \
                <br><br><br><br> \
        Our mission is to provide a platform for individuals & organizations to streamline the process of \
        documenting and anaylzing meetings to extract insights.</p>
         """, unsafe_allow_html=True)
    

with col2:

    st_lottie(
        "https://lottie.host/be93b7e7-74ac-46a8-bd3b-715dd9f7fb3c/f05zLQNZsY.json",
        speed=1,
        height=300,
        reverse=False,
        loop=True,
    )

    image_url = f"https://raw.githubusercontent.com/miketown77/MeetingGPT_Streamlit/master/images/Flow_Diagram_Home.png"

    st.image(image_url, use_column_width=True)



