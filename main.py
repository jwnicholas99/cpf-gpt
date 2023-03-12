import os
from dotenv import load_dotenv
import streamlit as st

from langchain import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQAWithSourcesChain

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
        vectorstore=vectorstore,
        return_source_documents=True
    )
    return chain
    
def search_docs(vectorstore, question):
    return vectorstore.similarity_search(
        question, k=4
    )

def query(chain, question):
    # Source documents are stored in source_documents in response
    return chain({"question": question}, return_only_outputs=True)

# App
load_dotenv()
vectorstore = load_vectorstore("./index")
chain = load_chain(vectorstore)

st.header("`CPF-GPT`")
st.info("`Hello! I am a ChatGPT connected to the Singapore CPF 1953 Act.`")
question = st.text_input("`Please ask a question:` ")

if question:
    response = query(chain, question)

    # Display answer
    st.info("`%s`"%response['answer'])

    # Display sources
    for source_doc in response['source_documents']:
        st.info("`%s`"%source_doc)