import streamlit as st
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import CacheBackedEmbeddings, OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
import time
import streamlit as st
import openai
import os
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import pygame

st.set_page_config(
    page_title="MixedGPT",
    page_icon="📃",
)
API_KEY = os.getenv("OPENAI_API_KEY")

def embed_file(file):
    file_content = file.read()
    file_path = f"./.cache/files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    cache_dir = LocalFileStore(f"./.cache/embeddings/{file.name}")
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader("./files/chapter_one.txt")
    docs = loader.load_and_split(text_splitter=splitter)
    embeddings = OpenAIEmbeddings()
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
    vectorstore = FAISS.from_documents(docs, cached_embeddings)
    retriever = vectorstore.as_retriever()
    return retriever

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

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        st.session_state["messages"].append({"message": message, "role": role})

def paint_history():
    for message in st.session_state["messages"]:
        send_message(
            message["message"],
            message["role"],
            save=False,
        )

st.title("🧑‍💻JS에듀 온라인 회화선생💬")

st.markdown(
    """
Welcome🤖!
"""
"""
파일을 업로드한 후 이를 AI와 대화할 수 있도록 만들고 있는 챗봇입니다.
잘 될지는 모르겠습니다.
"""
)

with st.sidebar:
    file = st.file_uploader(
        "Upload a .txt .pdf or .docx file",
        type=["pdf", "txt", "docx"],)
    audio_bytes = audio_recorder(icon_name="microphone")
    
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if audio_bytes:
    retriever = embed_file(file)
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()
    ##Save the Recorded File
    audio_location = "audio_file.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)
        
    #st.audio(audio_location)
    message = transcribe_text_to_voice(audio_location)
    if message:
        #Transcribe the saved file to text
        send_message(message, "human")
        #Use API to get an AI response
        api_response = chat_completion_call(message)
        send_message(api_response, "ai")

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
else:
    st.session_state["messages"] = []
        

    



