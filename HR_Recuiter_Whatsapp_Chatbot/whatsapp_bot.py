from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate 
from dotenv import load_dotenv
import os
import warnings
from pymongo import MongoClient
import requests

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["recruiter_ai"]
manage_job = db["manage_job"]

# Ignore all warnings
warnings.filterwarnings("ignore")

class ChatBot():
    def __init__(self):
        selected_job_id_str = os.getenv("SELECTED_JOB_ID", "")
        try:
            self.selected_job_id = int(selected_job_id_str)
        except ValueError:
            print(f"Error: 'SELECTED_JOB_ID' is not a valid integer. Defaulting to 0.")
            self.selected_job_id = 0

        print(f"Selected Job ID: {self.selected_job_id}")

        documents = manage_job.find({"selected_job_id": self.selected_job_id})
        documents_list = list(documents)

        # Combine all fields into a single string
        text_data = "\n".join([
            "\n".join([f"{key}: {value}" for key, value in document.items() if key != "selected_job_id"])
            for document in documents_list
        ])

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=4)
        docs = text_splitter.split_text(text_data)
        embeddings = HuggingFaceEmbeddings()
        self.vectorstore = FAISS.from_texts(texts=docs, embedding=embeddings)

        repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.2"
        self.llm = HuggingFaceHub(
            repo_id=repo_id, model_kwargs={"temperature": 0.8, "top_p": 0.8, "top_k": 50}, huggingfacehub_api_token=os.getenv('HUGGINGFACE_API_KEY')
        )

        self.template = """
        You are an HR recruiter chatbot. If the user greets you, respond politely and inform them that you are here to assist with HR and recruitment questions.
        If the user responds with "Yes," provide details about job opportunities and ask when they would like to schedule an interview or inquire about anything related. /
        If they respond with "No," thank them for their time and response.
        If the user asks a question about HR or recruitment, use the provided context to answer the question.
        For questions outside the scope of HR and recruitment, respond politely with: "Please contact hr@gmail.com for any other queries.""

        You should respond with short and concise answers, no longer than 2 sentences.

        Context: {context}
        Question: {question}
        Answer:
        """

        self.prompt = PromptTemplate(template=self.template, input_variables=["context", "question"])

        self.rag_chain = (
            {"context": self.vectorstore.as_retriever(),  "question": RunnablePassthrough()} 
            | self.prompt 
            | self.llm
            | StrOutputParser() 
        )
