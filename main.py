import os
from dotenv import load_dotenv

from langchain import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQAWithSourcesChain

class CPF_QA():
    def __init__(self, data_path, index_path):
        embeddings = OpenAIEmbeddings()

        if len(os.listdir(index_path)) == 0:
            
            with open('data/state_of_the_union.txt') as f:
                state_of_the_union = f.read()
                text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=0)
                texts = text_splitter.split_text(state_of_the_union)

                self.vectorstore = Chroma.from_texts(
                    texts, 
                    embeddings, 
                    metadatas=[{"source": f"{i}-pl"} for i in range(len(texts))],
                    persist_directory=index_path
                )
                self.vectorstore.persist()
        else:
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
    agent = CPF_QA("./data", "./index")
    print(agent.query("What was written in the article?"))