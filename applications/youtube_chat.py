from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def create_db_from_youtube_url(video_url, api_key):
    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()
    
    if not transcript:
        raise ValueError("The YouTube video does not have a transcript available.")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(transcript)
    
    if not docs:
        raise ValueError("Failed to split the transcript into documents.")
    
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    db = FAISS.from_documents(docs, embeddings)
    return db

def get_response_from_query_youtube(query, db, api_key, k=4):
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])
    llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=api_key, temperature=0)

    prompt_template = """
        You are a helpful assistant that can answer questions about YouTube videos based on its transcript.
        Answer the following question: {question}
        By searching the following video transcript: {docs}

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
