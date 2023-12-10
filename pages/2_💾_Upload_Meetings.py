import streamlit as st
import time
import boto3
import openai
import pandas as pd
import json
import uuid
import os
import gpt35
import post_process_output
import meeting_analytic_visuals
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import requests

os.environ["AWS_ACCESS_KEY_ID"] = st.secrets['AWS_ACCESS_KEY_ID']
os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets['AWS_SECRET_ACCESS_KEY']
os.environ["AWS_DEFAULT_REGION"] = st.secrets['AWS_DEFAULT_REGION']

# AWS Transcribe Functions
def upload_to_s3(uploaded_file, bucket_name, object_name=None):
    s3_client = boto3.client('s3')
    if object_name is None:
        object_name = uploaded_file.name

    s3_client.upload_fileobj(uploaded_file, bucket_name, object_name)
    return f"s3://{bucket_name}/{object_name}"


# Function for processing transcribe result with speaker identification
@st.cache_data
def convert_to_text(data):
    text_content = ""
    current_speaker = None
    sentence = ""

    for item in data['results']['items']:
        if item['type'] == 'pronunciation':
            speaker_label = item['speaker_label'] if 'speaker_label' in item else "Unknown"
            # Handle speaker change
            if current_speaker is not None and speaker_label != current_speaker:
                text_content += f"\n{current_speaker}: {sentence.strip()}"
                sentence = ""
            current_speaker = speaker_label
            sentence += item['alternatives'][0]['content'] + " "
        elif item['type'] == 'punctuation':
            sentence += item['alternatives'][0]['content']
            if item['alternatives'][0]['content'] in [".", "?", "!"]:
                text_content += f"\n{current_speaker}: {sentence.strip()}"
                sentence = ""

    if sentence.strip():
        text_content += f"\n{current_speaker}: {sentence.strip()}"

    return text_content

def download_and_extract_transcript(transcript_uri):
    # Use the requests module to get the content of the URL
    response = requests.get(transcript_uri)

    # Check if the request was successful
    if response.status_code == 200:
        transcript_json = response.json()
        transcript = transcript_json
        return transcript
    else:
        raise Exception(f"Failed to download transcript: {response.status_code}")

@st.cache_data
def transcribe(uploaded_file, bucket_name):
    # Initialize the Boto3 AWS Transcribe client
    transcribe_client = boto3.client('transcribe')

    # Create a unique name for the transcription job
    job_name = "transcription_" + str(uuid.uuid4())

    s3_uri = upload_to_s3(uploaded_file, bucket_name)

    # Start the transcription job
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat=uploaded_file.type.split('/')[1],
        LanguageCode='en-US',
        Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 5,
            }
    )

    # Update progress bar while waiting for the job to complete
    while True:
        time.sleep(10)
        status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            return download_and_extract_transcript(transcript_uri)
        elif status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
            st.error("Transcription job failed.")
            break

    return None

# Streamlit Interface
openai.api_key = st.secrets['OPEN_API_KEY']
bucket_name = st.secrets['AWS_BUCKET_NAME']  


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

st.set_page_config(page_title="MeetingGPT :spiral_note_pad:", page_icon=":spiral_note_pad:", layout="wide")


st.title(":blue[MeetingGPT] 📋📈📊")

font_size_style = """
    <style>
        .custom-font-size {
            font-size: 20px;  /* Replace with your desired font size */
        }
    </style>
"""

# Display markdown text with the specified style
st.markdown(font_size_style, unsafe_allow_html=True)

st.markdown("""
         <span class='custom-font-size'> <i>MeetingGPT</i> is a product designed to take in a meeting transcript
         or audio/video file and generate the following features:</span>

         <span class='custom-font-size'> 1. <b>Abstract Summary</b> - Succinct summary of the uploaded meeting<br></span>
         <span class='custom-font-size'> 2. <b>Action Items</b> - List of action items identified in the meeting & who they were assigned to<br></span>
         <span class='custom-font-size'> 3. <b>Key Topics</b> - Bar chart displaying the main topics discussed in order of % of time discussed<br></span>
         <span class='custom-font-size'> 4. <b>Speaking Time</b> - Pie Chart displaying distribution of speaking time across participants<br></span>
         <span class='custom-font-size'> 5. <b>Sentiment</b> - 1-word sentiment for meeting labeled by color as Positive (Green), Neutral (Gray) or Negative (Red)</span>
         """, unsafe_allow_html=True)

user_input = st.file_uploader(" ### Upload a Meeting Transcript or Meeting Video File for Processing:", on_change=change_user_input_state,
                              type=['txt', 'mp3', 'mp4', 'wav', 'avi', 'mov', 'mkv', 'flv', 'wmv'])

if st.session_state["response"] == "Incomplete":
    st.session_state['messages'] = []

if st.session_state["processing"] == "Ready":
    st.markdown("### :blue[MeetingGPT] Processing 📋📈📊")
    if user_input is not None:
        file_details = {"filename":user_input.name,
                "filetype":user_input.type,
                "filesize":user_input.size}
        # st.write(file_details)
        file_name = user_input.name
        if user_input.type == "text/plain":
            progress_bar = st.progress(0)
            raw_text = str(user_input.read(), "utf-8")
            raw_text = user_input_cache(raw_text)
            input_tokens, output_tokens, answer, response_time = first_api_call(raw_text)
            progress_bar.progress(25)
            reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time = second_api_call(answer)
            progress_bar.progress(50)
            df = pd.DataFrame({"meeting_id": [file_name], "final_response": [reformat_answer]})
            df, main_topics_df, engagement_df = reformat_df(df)
            progress_bar.progress(75)
            fig = meeting_analytic_visuals.generate_website_visual_images_only(df,main_topics_df,engagement_df)
            progress_bar.progress(100)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('### Abstract Summary:')
                st.markdown(df['Summary_Clipped'].iloc[0])
            with col2:
                st.markdown('### Action Items:')
                st.markdown(df['ActionItems_Clipped'].iloc[0])
            st.plotly_chart(fig)
            st.session_state['response'] = "Complete"
        if user_input.type in ['audio/mpeg', 'video/mp4', 'audio/wav', 'video/avi', 'video/mov', 'video/mkv', 'video/flv', 'video/wmv']:
            progress_bar = st.progress(0)
            raw_text = None
            transcribe_text = transcribe(user_input, bucket_name)
            try:
                raw_text = convert_to_text(transcribe_text)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing transcription result: {e}")
                print("Error parsing transcription result:", e)
                raw_text = ""  # or handle the error appropriately
            progress_bar.progress(20)
            input_tokens, output_tokens, answer, response_time = first_api_call(raw_text)
            progress_bar.progress(40)
            reformat_input_tokens, reformat_output_tokens, reformat_answer, reformat_response_time = second_api_call(answer)
            progress_bar.progress(60)
            df = pd.DataFrame({"meeting_id": [file_name], "final_response": [reformat_answer]})
            df, main_topics_df, engagement_df = reformat_df(df)
            progress_bar.progress(80)
            fig = meeting_analytic_visuals.generate_website_visual_images_only(df,main_topics_df,engagement_df)
            progress_bar.progress(100)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('### Abstract Summary:')
                st.markdown(df['Summary_Clipped'].iloc[0])
            with col2:
                st.markdown('### Action Items:')
                st.markdown(df['ActionItems_Clipped'].iloc[0])
            st.plotly_chart(fig)
            st.session_state['response'] = "Complete"

if st.session_state['response'] == "Complete":
    st.markdown("## :blue[MeetingGPT] :orange[ChatBot] - Ask questions about " +str(file_name))

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
