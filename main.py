import os
from dotenv import load_dotenv
import streamlit as st

from langchain import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQAWithSourcesChain

st.set_page_config(page_title="CPF.gpt")

@st.cache_resource
def load_vectorstore(index_path):
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        embedding_function=embeddings, 
        persist_directory=index_path
    )
    return vectorstore

@st.cache_resource
def load_chain(_vectorstore):
    chain = VectorDBQAWithSourcesChain.from_chain_type(
        OpenAI(model_name="gpt-3.5-turbo", temperature=0), 
        chain_type="stuff", 
        vectorstore=_vectorstore,
        return_source_documents=True
    )
    return chain
    
def search_docs(vectorstore, question):
    return vectorstore.similarity_search(
        question, k=4
    )

@st.cache_data
def query(_chain, question):
    # Source documents are stored in source_documents in response
    return chain({"question": question}, return_only_outputs=True)

# App
load_dotenv()
vectorstore = load_vectorstore("./index")
chain = load_chain(vectorstore)

st.title("CPF:violet[.gpt]")
st.write(
    """
    [![Star](https://img.shields.io/github/stars/jwnicholas99/cpf-gpt.svg?logo=github&style=social)](https://gitHub.com/jwnicholas99/cpf-gpt)
    [![Follow](https://img.shields.io/twitter/follow/jwnicholas99?style=social)](https://www.twitter.com/jwnicholas99)
    """
)

st.write(
"""
GPT3-powered question and answer for the
[Singapore CPF 1953 Act](https://sso.agc.gov.sg/Act/CPFA1953) (as of 12 March 2023).
This uses [LangChain](https://github.com/hwchase17/langchain) to interface with
GPT3 and [Chroma](https://github.com/chroma-core/chroma) as the vectorstore. 
""")
st.subheader("Ask your question below :speech_balloon: ")
question = st.text_input(
    "Empty label", 
    placeholder="Can I use my CPF funds to pay for my HDB flat?",
    label_visibility="collapsed")

if question:
    response = query(chain, question)

    # Display answer
    st.subheader("Answer")
    st.write(f"{response['answer']}")

    # Display sources
    st.subheader("Sources")
    for source_doc in response['source_documents']:
        st.info(f"""
        {source_doc}""")