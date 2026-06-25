import os
import sys
import tempfile

import streamlit as st

# Ensure root directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import ai_helper
from utils.i18n import t
from utils.navigation import initialize_page

# 1. Initialize Page and Sidebar
initialize_page(t("rag_assistant"), "📄")

# ── PAGE HEADER ─────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card" style="padding:28px 36px;">
    <h1>📄 {t("rag_assistant")}</h1>
    <p style="color:#94a3b8;">
        {t("rag_subtitle")}
    </p>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ── FILE UPLOADER ───────────────────────────────────────────
upl_pdf_lbl = t("upload_fitness_pdf")
uploaded_file = st.file_uploader(upl_pdf_lbl, type=["pdf"])

if uploaded_file:
    # Save uploaded file to temp path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    with st.spinner("Processing PDF..."):
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(docs)

            st.success(
                f"✓ {t('pdf_processed')} {t('success')}! Created {len(chunks)} {t('pdf_chunks')}."
            )
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            st.stop()

    # ── RETRIEVER SETUP (ROBUST FALLBACKS) ───────────────────
    retriever = None
    provider = st.session_state.ai_provider
    api_key = st.session_state.api_key

    # Attempt vector embeddings based on active provider
    if provider == "ollama":
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_ollama import OllamaEmbeddings

            embeddings = OllamaEmbeddings(model="nomic-embed-text")
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        except Exception:
            # Fallback warning
            st.warning(
                "⚠️ 'nomic-embed-text' model not found in Ollama. Falling back to keyword search (TF-IDF) for safety."
            )

    elif provider == "openai" and api_key:
        try:
            from langchain_community.embeddings import OpenAIEmbeddings
            from langchain_community.vectorstores import FAISS

            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        except Exception:
            pass

    # Safe Local Fallback: TF-IDF Keyword Retriever (needs no API keys or local models!)
    if retriever is None:
        try:
            from langchain_community.retrievers import TFIDFRetriever

            retriever = TFIDFRetriever.from_documents(chunks)
        except Exception as tfidf_err:
            st.error(f"Failed to initialize search engine: {tfidf_err}")
            st.stop()

    # ── QUESTION ANSWERING ──────────────────────────────────
    q_pdf_lbl = t("ask_about_pdf")
    question = st.text_input(
        q_pdf_lbl, placeholder="e.g. What is the recommended protein intake in this guide?"
    )

    if question:
        with st.spinner(t("loading")):
            try:
                # Retrieve relevant documents
                if hasattr(retriever, "get_relevant_documents"):
                    results = retriever.get_relevant_documents(question)
                else:
                    results = retriever.similarity_search(question, k=3)

                context = "\n\n".join(doc.page_content for doc in results)

                prompt = f"""
Context from uploaded document:
{context}

Question:
{question}

Based ONLY on the context provided above, answer the question. If the answer is not found in the context, politely state that it's not mentioned in the document.
"""
                sys_p = "You are a professional research assistant. Answer concisely and accurately based on the document context."
                response = ai_helper.get_ai_response(prompt, sys_p, max_tokens=1500)

                st.markdown(ai_helper.provider_badge(), unsafe_allow_html=True)
                st.markdown(
                    f"""
                <div class="info-card" style="padding:20px;border-left:4px solid #10b981;">
                    <h4 style="margin-top:0;color:#10b981;">📋 PDF Assistant Answer</h4>
                    <div>{response}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            except Exception as qa_err:
                st.error(f"RAG QA Error: {qa_err}")

    # Cleanup temp file
    try:
        os.unlink(pdf_path)
    except Exception:
        pass
