import streamlit as st
from st_functions import st_button, load_css

st.session_state["response"] = "Incomplete"

st.title(":blue[MeetingGPT] - Privacy Notice 📋📈📊")
load_css()

icon_size=8

st_button('', "https://docs.google.com/document/d/1h3hvs7o-uPTZ5R6QPRmngyTGok0RbX1JEWdo1J7fpdo/edit?usp=sharing", "Full Privacy Policy Document", icon_size)

st.markdown("### **Mission Statement**")
st.markdown("""MeetingGPT is committed to enhancing the efficiency and effectiveness of virtual meetings by providing \
            a cutting-edge NLP solution. Our mission is to streamline the process of creating high-level summaries, \
            actionable items, and engagement analytics, making it easier for individuals and organizations to extract key insights. \
            We understand the importance of privacy and ethics in this process and are dedicated to safeguarding the information we collect.""")

st.markdown("### **Overview**")
st.markdown("""MeetingGPT is a software solution designed to save time and derive insights from virtual meetings by outputting actionable items 
            from the meeting as well curatable options by user. This privacy notice outlines how MeetingGPT collects, uses, and protects your 
            information. By implementing these practices, we aim to collect your data while respecting your privacy rights and maintaining your
            trust in MeetingGPT. We also recommend consulting with legal experts to ensure compliance with relevant privacy regulations and standards. 
            Your privacy is important to us, and we are committed to safeguarding your data.""")

