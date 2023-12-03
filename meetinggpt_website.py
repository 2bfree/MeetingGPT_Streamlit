import streamlit as st
import time
import os
import openai
import gpt35
import llama
import pandas as pd
import post_process_output
import meeting_analytic_visuals
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

openai.api_key = st.secrets['OPEN_API_KEY']

if "input" not in st.session_state:
    st.session_state["input"] = "not done"

def change_user_input_state():
    st.session_state["input"] = "done"

st.set_page_config(page_title="MeetingGPT", page_icon=":tada", layout="wide")

st.markdown(" # Meeting GPT - Meeting Analytics App")
st.markdown(" #### UCB MIDS Capstone Team: Siva Chamiraju, Francis Lee, Chase Madson, Michael Townsend")
st.markdown("""
         _MeetingGPT_ is a product designed to take in a meeting transcript
         or video file and generate the following features:

         1. **Abstract Summary** - Succinct summary of the uploaded meeting
         2. **Action Items** - List of action items identified in the meeting & who they were assigned to
         3. **Key Topics** - Bar chart displaying the main topics discussed in order of % of time discussed
         4. **Speaking Time** - Pie Chart displaying distribution of speaking time across participants
         5. **Sentiment** - One-word sentiment classification for meeting labeled by color as Positive (Green), Neutral (Gray) or Negative (Red)
         
         """)

user_input = st.file_uploader(" ### Upload a Meeting Transcript or Meeting Video File:", on_change=change_user_input_state,
                              type=['txt', 'mp3', 'mp4', 'wav', 'avi', 'mov', 'mkv', 'flv', 'wmv'])


if st.session_state["input"] == "done":
    progress_bar = st.progress(0)

    for perc_completed in range(100):
        time.sleep(0.01)
        progress_bar.progress(perc_completed+1)

    st.success("Transcript / Video Uploaded Successfully")

    # st.session_state['type'] = st.radio("Which Model would you like to ask", ["GPT3.5 Turbo", "Llama2"])
    # if st.session_state['type'] == "GPT3.5 Turbo":
    st.markdown("# MeetingGPT Processing")
    if st.button("Process"):
        if user_input is not None:
            file_details = {"filename":user_input.name,
                    "filetype":user_input.type,
                    "filesize":user_input.size}
            # st.write(file_details)
            if user_input.type == "text/plain":
                raw_text = str(user_input.read(), "utf-8")
                # st.write("Raw Transcript:")
                # st.write(raw_text)
                input_tokens, output_tokens, answer, response_time = gpt35.gpt35_meeting_analytics(raw_text)
                # st.write("Original Answer:")
                # st.write(answer)
                reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time = gpt35.reformat_gpt35(answer)
                # st.write("Reformatted Answer:")
                # st.write(reformat_answer)
                df = pd.DataFrame({"meeting_id": [user_input.name], "final_response": [reformat_answer]})
                df, main_topics_df, engagement_df = post_process_output.reformat_for_visuals(df)
                fig = meeting_analytic_visuals.generate_website_visual(df, main_topics_df, engagement_df)
                st.plotly_chart(fig)
                    
    # if st.session_state['type'] == "Llama2":
    #     st.markdown("# Llama Model processing")
    #     if st.button("Process"):
    #         if user_input is not None:
    #             file_details = {"filename":user_input.name,
    #                     "filetype":user_input.type,
    #                     "filesize":user_input.size}
    #             # st.write(file_details)
    #             if user_input.type == "text/plain":
    #                 raw_text = str(user_input.read(), "utf-8")
    #                 input_tokens, output_tokens, answer, response_time = llama.llama_meeting_analytics(raw_text)
    #                 reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time = gpt35.reformat_gpt35(answer)
    #                 df = pd.DataFrame({"meeting_id": [user_input.name], "final_response": [reformat_answer]})
    #                 df, main_topics_df, engagement_df = post_process_output.reformat_for_visuals(df)
    #                 fig = meeting_analytic_visuals.generate_website_visual(df, main_topics_df, engagement_df)
    #                 st.plotly_chart(fig)
