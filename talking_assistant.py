# pip install streamlit
# pip install audio-recorder-streamlit
# pip install openai

import streamlit as st
import openai
import os
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import pygame

API_KEY = os.getenv("OPENAI_API_KEY")

def transcribe_text_to_voice(audio_location):
    client = OpenAI(api_key=API_KEY)
    audio_file= open(audio_location, "rb")
    transcript = client.audio.transcriptions.create(language='en', model="whisper-1", file=audio_file)
    return transcript.text

def chat_completion_call(text):
    client = OpenAI(api_key=API_KEY)
    messages = [{"role": "user", "content": text}]
    response = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=messages)
    return response.choices[0].message.content

def text_to_speech_ai(speech_file_path, api_response):
    client = OpenAI(api_key=API_KEY)
    response = client.audio.speech.create(model="tts-1",voice="alloy",input=api_response)
    response.stream_to_file(speech_file_path)
   
st.title("🧑‍💻 JS에듀 온라인 선생 💬")

"""
Hi🤖 just click on the voice recorder and let me know how I can help you today?
"""

audio_bytes = audio_recorder(icon_name="microphone")
if audio_bytes:
    ##Save the Recorded File
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)
    #st.audio(audio_location)

    #Transcribe the saved file to text
    text = transcribe_text_to_voice(audio_location)
    st.write(text)

    #Use API to get an AI response
    api_response = chat_completion_call(text)
    st.write(api_response)

    # Read out the text response using tts
    speech_file_path = 'audio_response.mp3'
    text_to_speech_ai(speech_file_path, api_response)
    #st.audio(speech_file_path)
    pygame.mixer.init()
    pygame.mixer.music.load(speech_file_path)
    pygame.mixer.music.play()
    clock = pygame.time.Clock()
    while pygame.mixer.music.get_busy():
        clock.tick(30)
    pygame.mixer.quit()
    try:
        os.remove(audio_location)
        os.remove(speech_file_path)
    except PermissionError:
        st.write("We can't delete the files.")

    

