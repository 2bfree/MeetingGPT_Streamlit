import streamlit as st
from st_functions import st_button, load_css

st.session_state["response"] = "Incomplete"

st.title(":blue[MeetingGPT] - Product Demo 📋📈📊")
load_css()

icon_size = 20

st_button('youtube', "https://www.youtube.com/watch?v=q0RfchmxcOI", "Product Demo", icon_size)

infrastructure_url = f"https://raw.githubusercontent.com/miketown77/MeetingGPT_Streamlit/master/images/infrastructure.png" 

# Set the desired width and height of the image
image_width = 750
image_height = 550

# Use st.markdown with CSS styling to set the width and height
st.markdown(
    f'<div style="text-align:center;"><img src="{infrastructure_url}" alt="Your Image Caption" style="width: {image_width}px; height: {image_height}px; display: block; margin: auto;"></div>',
    unsafe_allow_html=True
)




