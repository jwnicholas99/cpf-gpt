import os
from dotenv import load_dotenv
import streamlit as st

from langchain import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQAWithSourcesChain

class CPF_QA():
    def __init__(self, index_path):
        embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            embedding_function=embeddings, 
            persist_directory=index_path
        )
        self.chain = VectorDBQAWithSourcesChain.from_chain_type(
            OpenAI(model_name="gpt-3.5-turbo", temperature=0), 
            chain_type="stuff", 
            vectorstore=self.vectorstore,
            return_source_documents=True
        )
    
    def search_docs(self, question):
        return self.vectorstore.similarity_search(
            question, k=4
        )

    def query(self, question):
        # Source documents are stored in source_documents in response
        return self.chain({"question": question}, return_only_outputs=True)

if __name__=='__main__':
    load_dotenv()
    agent = CPF_QA("./index")
    #print(agent.search_docs("Can the CPF funds be used to pay for Medishield?"))
    print(agent.query("What is the employer's CPF contribution for somebody who is 56 years old?"))