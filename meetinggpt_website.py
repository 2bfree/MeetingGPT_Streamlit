import streamlit as st
import time
import os
import openai
import gpt35
import pandas as pd
import post_process_output
import meeting_analytic_visuals
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

openai.api_key = st.secrets['OPEN_API_KEY']

if "response" not in st.session_state:
    st.session_state["response"] = "Incomplete"

if "processing" not in st.session_state:
    st.session_state["processing"] = "Not Ready"

def change_user_input_state():
    st.session_state["response"] = "Incomplete"
    st.session_state["processing"] = "Ready"

@st.cache_data
def user_input_cache(input):
    return input

@st.cache_data
def first_api_call(transcript):
    input_tokens, output_tokens, answer, response_time = gpt35.gpt35_meeting_analytics(raw_text)
    return input_tokens, output_tokens, answer, response_time

@st.cache_data
def second_api_call(transcript):
    reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time = gpt35.reformat_gpt35(answer)
    return reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time

@st.cache_data
def reformat_df(df_in):
    df, main_topics_df, engagement_df = post_process_output.reformat_for_visuals(df_in)
    return df, main_topics_df, engagement_df

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


user_input = st.file_uploader(" ### Upload a Meeting Transcript or Meeting Video File for Processing:", on_change=change_user_input_state,
                              type=['txt', 'mp3', 'mp4', 'wav', 'avi', 'mov', 'mkv', 'flv', 'wmv'])

if st.session_state["response"] == "Incomplete":
    st.session_state['messages'] = []

if st.session_state["processing"] == "Ready":
    st.markdown("# MeetingGPT Processing")
    if user_input is not None:
        file_details = {"filename":user_input.name,
                "filetype":user_input.type,
                "filesize":user_input.size}
        # st.write(file_details)
        if user_input.type == "text/plain":
            progress_bar = st.progress(0)
            raw_text = str(user_input.read(), "utf-8")
            file_name = user_input.name
            raw_text = user_input_cache(raw_text)
            input_tokens, output_tokens, answer, response_time = first_api_call(raw_text)
            progress_bar.progress(25)
            reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time = second_api_call(answer)
            progress_bar.progress(50)
            df = pd.DataFrame({"meeting_id": [file_name], "final_response": [reformat_answer]})
            df, main_topics_df, engagement_df = reformat_df(df)
            progress_bar.progress(75)
            fig = meeting_analytic_visuals.generate_website_visual(df,main_topics_df,engagement_df)
            progress_bar.progress(100)
            st.plotly_chart(fig)
            st.session_state['response'] = "Complete"

if st.session_state['response'] == "Complete":
    st.title("ChatBot for " + str(user_input.name))

    if "messages" not in st.session_state:
        st.session_state['messages'] = []

    for message in st.session_state.messages:
        with st.chat_message(message.get("role")):
            st.markdown(message.get("content"))
    
    prompt = st.chat_input("Ask a question about the Meeting")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            input_query = gpt35.qa_extraction_gpt35_input_query(prompt, raw_text)
            for response in openai.ChatCompletion.create(
                                model="gpt-3.5-turbo-16k",
                                temperature=0,
                                messages=input_query,
                                stream=True
                                ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "| ")
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response}) 
