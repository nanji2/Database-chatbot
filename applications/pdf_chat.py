import tempfile
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


def create_db_from_pdf(pdf_files, api_key):
    docs = []
    temp_dir = tempfile.TemporaryDirectory()
    for file in pdf_files:
        temp_file_path = os.path.join(temp_dir.name, file.name)
        with open(temp_file_path, "wb") as f:
            f.write(file.getvalue())
        loader = PyPDFLoader(temp_file_path)
        docs.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    db = FAISS.from_documents(docs, embeddings)
    return db


def get_response_from_query_pdf(query, db, api_key, k=4):
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])
    llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=api_key, temperature=0)

    prompt_template = """
        You are a helpful assistant that can answer questions about the information presented in PDF files.
        Answer the following question: {question}
        By searching the following documents from the PDF file: {docs}

        Do only use factual information from the transcript and do not make up any information.
        If you have insufficient information to answer the question, please say so.

        Your answer should be verbose and detailed.
        """
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template=prompt_template
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(question=query, docs=docs_page_content)
    return response
