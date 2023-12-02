import streamlit as st
import time
import os
import openai
from transformers import AutoTokenizer
import gpt35
import llama
import pandas as pd
import post_process_output
import meeting_analytic_visuals
from io import BytesIO
from PIL import Image
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import textwrap
from html2image import Html2Image
import os

openai.api_key = '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'

if "input" not in st.session_state:
    st.session_state["input"] = "not done"

def change_user_input_state():
    st.session_state["input"] = "done"

st.set_page_config(page_title="MeetingGPT", page_icon=":tada", layout="wide")

# def check_uploaded_file(file_path):
#     _, ext = os.path.splitext(file_path)
#     ext = ext.lower()
#     return ext in ['.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv', '.flv', '.wmv']

## ---- HEADER SECTION -----
# st.subheader("Hi, I am Sven :wave:")

# col1, col2, col3 = st.columns([1,2,1])

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

    # def handle_click(new_type):
    #     st.session_state.type = new_type

    st.session_state['type'] = st.radio("Which Model would you like to ask", ["GPT3.5 Turbo", "Llama2"])
    # change = st.button("Change", on_click=handle_click)

    if st.session_state['type'] == "GPT3.5 Turbo":
        st.markdown("# GPT3.5 Turbo Model processing")
        if st.button("Process"):
            if user_input is not None:
                file_details = {"filename":user_input.name,
                        "filetype":user_input.type,
                        "filesize":user_input.size}
                # st.write(file_details)
                if user_input.type == "text/plain":
                    raw_text = str(user_input.read(), "utf-8")
                    st.write("Raw Transcript:")
                    st.write(raw_text)
                    input_tokens, output_tokens, answer, response_time = gpt35.gpt35_meeting_analytics(raw_text)
                    st.write("Original Answer:")
                    st.write(answer)
                    reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time = gpt35.reformat_gpt35(answer)
                    st.write("Reformatted Answer:")
                    st.write(reformat_answer)
                    df = pd.DataFrame({"meeting_id": [user_input.name], "final_response": [reformat_answer]})
                    df, main_topics_df, engagement_df = post_process_output.reformat_for_visuals(df)
                    fig = meeting_analytic_visuals.generate_website_visual(df, main_topics_df, engagement_df)
                    # Display the image using Streamlit
                    # st.image(img, use_container_width=True)
                    st.plotly_chart(fig)
                    # st.write(reformat_answer)

                    # with open(full_file_path, "r", encoding="utf-8") as file:
                    #     html_content = file.read()
                    
                    # Display HTML using st.markdown
                    # st.markdown(html_content, unsafe_allow_html=True)

                    # img = Image.open(full_file_path)
                    # st.image(img, use_column_width=True)

                    ## Raw Output
                    # st.write(reformat_answer)

                    # Display the image in your Streamlit app
                    # st.image(BytesIO(image_output), use_column_width=True)
                    
    if st.session_state['type'] == "Llama2":
        st.markdown("# Llama Model processing")
        if st.button("Process"):
            if user_input is not None:
                file_details = {"filename":user_input.name,
                        "filetype":user_input.type,
                        "filesize":user_input.size}
                # st.write(file_details)
                if user_input.type == "text/plain":
                    raw_text = str(user_input.read(), "utf-8")
                    input_tokens, output_tokens, answer, response_time = llama.llama_meeting_analytics(raw_text)
                    reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time = gpt35.reformat_gpt35(answer)
                    df = pd.DataFrame({"meeting_id": [user_input.name], "final_response": [reformat_answer]})
                    df, main_topics_df, engagement_df = post_process_output.reformat_for_visuals(df)
                    fig = meeting_analytic_visuals.generate_website_visual(df, main_topics_df, engagement_df)
                    # Display the image using Streamlit
                    # st.image(img, use_container_width=True)
                    st.plotly_chart(fig)
                    # with open(full_file_path, "r", encoding="utf-8") as file:
                    #     html_content = file.read()
                    
                    # Display HTML using st.markdown
                    # st.markdown(html_content, unsafe_allow_html=True)

                    # img = Image.open(full_file_path)
                    # st.image(img, use_column_width=True)

                    ## Raw Output
                    # st.write(reformat_answer)

                    # Display the image in your Streamlit app
                    # st.image(BytesIO(image_output), use_column_width=True)

    # check_file_type = check_uploaded_file(user_input)
    # if check_file_type:
    #     st.markdown("### File Identified as Video -- Running Transcription")

    # else:
    #     st.markdown("### File Identified as Text -- Sending Transcript to LLM for processing")

    


# st.title("Meeting GPT - W210 Capstone Project")
# st.subheader("By: Siva Chamiraju, Francis Lee, Chase Madson, Michael Townsend")

# st.write("""
#          MeetingGPT is a product designed to take in a meeting transcript
#          or video file and generate the following features:

#          1. Abstract Summary - Succinct summary of the uploaded meeting
#          2. Action Items - List of action items identified in the meeting & who they were assigned to
#          3. Key Topics - Bar chart displaying the main topics discussed in order of % of time discussed
#          4. Speaking Time - Pie Chart displaying distribution of speaking time across participants
#          5. Sentiment - One-word sentiment classification for meeting labeled by color as Positive (Green), Neutral (Gray) or Negative (Red)
         
#          """)

# st.write('----')
# left_column, right_column = st.columns(2)



# with left_column:
#     st.header("What I do")
#     st.write("##")
#     st.write(
#         """
#         On my YouTube channel I am creating tutorials for people
#         """
#     )