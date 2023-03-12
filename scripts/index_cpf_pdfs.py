import os
import PyPDF2
from dotenv import load_dotenv

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

INDEX_PATH = "../index"

load_dotenv("../.env")
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    embedding_function=embeddings, 
    persist_directory=INDEX_PATH
)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)

def pdf_to_texts(file_path):
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

    texts = []
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        page_text = page_text.replace(
            "Singapore Statutes Online Current version as at 12 Mar 2023 PDF created date on: 12 Mar 2023",
            ""
        )
        texts.append(page_text)
    pdf_file_obj.close()

    full_text = "".join(texts)
    texts = text_splitter.split_text(full_text)
    print(texts[0])
    return texts

def add_to_vectorstore(file_name, texts):
    vectorstore.add_texts(
        texts,
        metadatas=[{"source": f"{file_name}-chunk{i}"} for i in range(len(texts))],
    )

if __name__=="__main__":
    data_files = os.listdir("../data")
    for data_file in data_files:
        texts = pdf_to_texts(f"../data/{data_file}")
        add_to_vectorstore(data_file, texts)
