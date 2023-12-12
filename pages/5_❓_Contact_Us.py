import streamlit as st
from st_functions import st_button, load_css

st.session_state["response"] = "Incomplete"

st.title(":blue[MeetingGPT] - Contact Us 📋📈📊")
load_css()

st.markdown("### **Meet the UC Berkeley MIDS Capstone Team**")

full_team_url = f"https://github.com/miketown77/MeetingGPT_Streamlit/blob/master/images/Capstone_Team_Contact_Us.png?raw=true"

st.image(full_team_url, use_column_width=True)

col1, col2, col3, col4 = st.columns(4)

icon_size=8

with col1:
    st_button('linkedin', "https://www.linkedin.com/in/chasemadson/", "LinkedIn", icon_size)

with col2:
    st_button('linkedin', "https://www.linkedin.com/in/francis-lee10/", "LinkedIn", icon_size)

with col3:
    st_button('linkedin', "https://www.linkedin.com/in/michael-townsend-54775bb9/", "LinkedIn", icon_size)    

with col4:
    st_button('linkedin', "https://www.linkedin.com/in/sivaram-chamiraju-1714472/", "LinkedIn", icon_size) 
