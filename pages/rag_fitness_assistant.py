import streamlit as st
import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_ollama import (
    ChatOllama,
    OllamaEmbeddings
)

from langchain_community.vectorstores import Chroma

st.title(
    "📄 RAG Fitness Assistant"
)

uploaded_file = st.file_uploader(
    "Upload Fitness PDF",
    type="pdf"
)

if uploaded_file:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:

        tmp.write(
            uploaded_file.read()
        )

        pdf_path = tmp.name

    loader = PyPDFLoader(
        pdf_path
    )

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(
        docs
    )

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="./chroma_db"
    )

    question = st.text_input(
        "Ask about the PDF"
    )

    if question:

        results = vectorstore.similarity_search(
            question,
            k=3
        )

        context = "\n".join(
            [
                doc.page_content
                for doc in results
            ]
        )

        llm = ChatOllama(
            model="llama3.2"
        )

        prompt = f"""
        Context:
        {context}

        Question:
        {question}

        Answer:
        """

        response = llm.invoke(
            prompt
        )

        st.write(
            response.content
        )