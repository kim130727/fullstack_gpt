from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
import streamlit as st
from langchain.retrievers import WikipediaRetriever


st.set_page_config(
    page_title="QuizGPT",
    page_icon="❓",
)

st.title("TestGPT")

retriever = WikipediaRetriever()
docs = retriever.get_relevant_documents("hummus")
docs[0].metadata  # meta-information of the Document
