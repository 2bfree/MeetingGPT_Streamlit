import streamlit as st
from st_functions import st_button, load_css

st.session_state["response"] = "Incomplete"

st.title(":blue[MeetingGPT] - Contact Us 📋📈📊")
load_css()

st.markdown("### **Meet the UC Berkeley MIDS Capstone Team**")

col1, col2, col3, col4 = st.columns(4)

icon_size=8

chase_url = f"https://raw.githubusercontent.com/miketown77/MeetingGPT_Streamlit/74aec8f060f53dbdf0f06cd7abe2164812c8c630/images/Chase.png"
francis_url = f"https://raw.githubusercontent.com/miketown77/MeetingGPT_Streamlit/74aec8f060f53dbdf0f06cd7abe2164812c8c630/images/Francis.png"
michael_url = f"https://raw.githubusercontent.com/miketown77/MeetingGPT_Streamlit/74aec8f060f53dbdf0f06cd7abe2164812c8c630/images/Michael.png"
siva_url = f"https://raw.githubusercontent.com/miketown77/MeetingGPT_Streamlit/74aec8f060f53dbdf0f06cd7abe2164812c8c630/images/Siva.png"

with col1:
    st.image(chase_url, use_column_width=True)
    st_button('linkedin', "https://www.linkedin.com/in/chasemadson/", "LinkedIn", icon_size)

with col2:
    st.image(francis_url, use_column_width=True)
    st_button('linkedin', "https://www.linkedin.com/in/francis-lee10/", "LinkedIn", icon_size)

with col3:
    st.image(michael_url, use_column_width=True)
    st_button('linkedin', "https://www.linkedin.com/in/michael-townsend-54775bb9/", "LinkedIn", icon_size)    

with col4:
    st.image(siva_url, use_column_width=True)
    st_button('linkedin', "https://www.linkedin.com/in/sivaram-chamiraju-1714472/", "LinkedIn", icon_size) 
