import streamlit as st
from rag import (
    read_pdf,
    chunk_text,
    get_embeddings,
    store_chunks,
    generate_answer
)

# App title
st.title("PDF RAG Chatbot")

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

# Process uploaded PDF
if uploaded_file:
    text = read_pdf(uploaded_file)
    chunks = chunk_text(text)
    embeddings = get_embeddings(chunks)
    store_chunks(chunks, embeddings)

    st.success("PDF processed successfully!")

# Ask question
question = st.text_input("Ask a question from PDF")

# Generate answer
if question:
    answer = generate_answer(question)

    st.write("Answer:")
    st.write(answer)
    #text
