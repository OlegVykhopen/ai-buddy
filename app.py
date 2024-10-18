import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Float feature initialization
float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi Dear! How do you feel today?"}
        ]
    if "audio_playing" not in st.session_state:
        st.session_state.audio_playing = False  # Tracks if audio is playing
    if "current_audio_file" not in st.session_state:
        st.session_state.current_audio_file = None  # Stores the current audio file path
    if "response_generated" not in st.session_state:
        st.session_state.response_generated = False  # Ensure response isn't regenerated on stop
    if "stop_audio_clicked" not in st.session_state:
        st.session_state.stop_audio_clicked = False  # Tracks if stop button was clicked

initialize_session_state()

st.title("Your Mood Buddy 🤖")

# Create footer container for the microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    # Write the audio bytes to a file
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

# Prevent response re-generation if Stop Audio button was clicked
if not st.session_state.stop_audio_clicked:
    # Check if a response has already been generated for the latest user input
    if st.session_state.messages[-1]["role"] != "assistant" and not st.session_state.response_generated:
        with st.chat_message("assistant"):
            with st.spinner("Thinking🤔..."):
                final_response = get_answer(st.session_state.messages)

            with st.spinner("Generating audio response..."):
                # Pass the clean version (without URLs) to the text-to-speech
                audio_file = text_to_speech(final_response)

                # Store the current audio file and flag response as generated
                st.session_state.current_audio_file = audio_file
                st.session_state.response_generated = True  # Mark response as generated

                # Play the generated audio only once
                st.session_state.audio_playing = True

            # Display the final response (with URLs) in text format
            st.write(final_response)

            # Append the response to the session state
            st.session_state.messages.append({"role": "assistant", "content": final_response})

# Stop audio functionality and control Stop button visibility
if st.session_state.audio_playing:
    if st.button("Stop Audio"):
        # This effectively stops the audio by removing it from the page
        st.session_state.audio_playing = False
        st.session_state.current_audio_file = None  # Clear the audio file
        st.session_state.stop_audio_clicked = True  # Flag stop button was clicked
        st.write("Audio stopped.")

# Autoplay audio only once per response and not on app reruns
if st.session_state.current_audio_file and st.session_state.audio_playing and not st.session_state.stop_audio_clicked:
    # Play the audio if it's not stopped and is currently playing
    autoplay_audio(st.session_state.current_audio_file)
    st.session_state.audio_playing = False  # Ensure it doesn't replay on reruns

# Ensure "Stop Audio" button is hidden when audio has stopped
if not st.session_state.audio_playing:
    st.session_state.current_audio_file = None  # Ensure audio is cleared

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")