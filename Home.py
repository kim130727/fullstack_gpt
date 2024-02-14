import streamlit as st

"hello" #magic

st.title("Hello world!")

st.write("how cool is that?") #st.write

st.selectbox(
    "Choose your model",
    (
        "GPT-3",
        "GPT-4",
    ),
)