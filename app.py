import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# CSS to hide Streamlit's top-right buttons and style the audio recorder button
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Style for the microphone button, using a GIF */
    .audio-recorder-element {
        background-image: url('https://media.giphy.com/media/3o7abldj0b3rxrZUxW/giphy.gif');  /* Replace with your own GIF URL */
        background-size: cover;
        background-repeat: no-repeat;
        width: 100px;  /* Adjust size as needed */
        height: 100px;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        display: block;
    }

    /* Hide the default microphone icon */
    .audio-recorder-element svg {
        display: none;
    }

    footer {visibility: hidden;}
    footer:after {
        content:'';
        visibility: hidden;
        display: none;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state for chat and audio
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi Dear! How do you feel today?"}
        ]
    if "audio_playing" not in st.session_state:
        st.session_state.audio_playing = False
    if "current_audio_file" not in st.session_state:
        st.session_state.current_audio_file = None
    if "response_generated" not in st.session_state:
        st.session_state.response_generated = False  # Ensure new response can be generated

initialize_session_state()

# Adjust the column width to make both left and right columns wider
left_col, right_col = st.columns([2, 5])  # Adjust this ratio to make the columns wider

# Microphone section in the left column with styled audio_recorder button
with left_col:
    audio_bytes = audio_recorder()  # Mic icon and audio recording widget in the left column

# Chat section in the right column
with right_col:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Handle audio transcription if a microphone input is received
if audio_bytes:
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)
        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with right_col:
                with st.chat_message("user"):
                    st.write(transcript)
            os.remove(webm_file_path)
            st.session_state.response_generated = False  # Allow response generation for new message

# Check if a response has already been generated for the latest user input
if st.session_state.messages[-1]["role"] != "assistant" and not st.session_state.response_generated:
    with right_col:  # Ensure response generation happens in the right column
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                final_response = get_answer(st.session_state.messages)
            with st.spinner("Generating audio response..."):
                audio_file = text_to_speech(final_response)
                st.session_state.current_audio_file = audio_file
                st.session_state.response_generated = True  # Mark response as generated
                autoplay_audio(audio_file)
                st.session_state.audio_playing = True
            st.write(final_response)
            st.session_state.messages.append({"role": "assistant", "content": final_response})

# Ensure the layout is structured with the chat on the right and mic on the left