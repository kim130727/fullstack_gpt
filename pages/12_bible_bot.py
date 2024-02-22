import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import CacheBackedEmbeddings, OpenAIEmbeddings
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.storage import LocalFileStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
import time
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import os
import pygame

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃",
)

API_KEY = os.getenv("OPENAI_API_KEY")

class ChatCallbackHandler(BaseCallbackHandler):
    message = ""

    def on_llm_start(self, *args, **kwargs):
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kwargs):
        save_message(self.message, "ai")

    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token
        self.message_box.markdown(self.message)

llm = ChatOpenAI(
    temperature=0.1,
    streaming=True,
    callbacks=[
        ChatCallbackHandler(),
    ],
)

@st.cache_resource(show_spinner="Embedding file...") #st.cache_data가 안되서 바꿔보았음
def embed_file(file):
    print({file.name})
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
    loader = UnstructuredFileLoader(f"./files/{file.name}")
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

def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)


def paint_history():
    for message in st.session_state["messages"]:
        send_message(
            message["message"],
            message["role"],
            save=False,
        )

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

def text_to_speech_ai(speech_file_path, api_response):
    client = OpenAI(api_key=API_KEY)
    response = client.audio.speech.create(model="tts-1",voice="alloy",input=api_response)
    response.stream_to_file(speech_file_path)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            AI 이름은 진산이입니다.
            주어진 context를 통해 AI와 Discussion를 진행합니다. Discussion은 A2 레벨로 진행합니다. 단어에 대한 설명을 해주고 문법을 교정해주기도 합니다. 답변하는 문장은 2개 이하입니다.
            
            Context: {context}
            """,
        ),
        ("human", "{question}"),
    ]
)

st.title("📖 성경공부 AI 비서")

st.subheader("소예언서 내용을 가지고 🤖진산AI와 대화해 봅시다.")
st.write("질문을 해주시고 답변이 이상하면 언제든지 성환이에게 이야기해주세요.")

with st.sidebar:
    file = st.file_uploader(
        "Upload a .txt .pdf or .docx file",
        type=["pdf", "txt", "docx"],
    )
    #audio_bytes = audio_recorder(icon_name="microphone")

if file:
    retriever = embed_file(file)
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()
    message = st.chat_input("Ask anything about your file...")
    #audio_location = "audio_file.wav"
    #with open(audio_location, "wb") as f:
    #    f.write(audio_bytes)
        
    #st.audio(audio_location)
    #message = transcribe_text_to_voice(audio_location)
    if message:
        pygame.mixer.quit()
        send_message(message, "human")
        
        chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
        )
        with st.chat_message("ai"):
            response = chain.invoke(message)
            try:
                speech_file_path = 'audio_response.mp3'
                text_to_speech_ai(speech_file_path, response.content)
                pygame.mixer.init()
                pygame.mixer.music.load(speech_file_path)
                pygame.mixer.music.play()
                clock = pygame.time.Clock()
                while pygame.mixer.music.get_busy():
                    clock.tick(30)
                pygame.mixer.quit()
            except:
                st.write("pass")
            try:
                os.remove('audio_response.mp3')
            except PermissionError:
                st.write("We can't delete the files.")
else:
    st.session_state["messages"] = []