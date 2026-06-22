from pypdf import PdfReader
import uuid
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
import os

# -------------------------------
# Setup models
# -------------------------------

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create vector DB client
client = chromadb.Client()

# Create collection to store PDF chunks
collection = client.get_or_create_collection("pdf_docs")

# Configure Groq API
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -------------------------------
# Read PDF
# -------------------------------
def read_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    return text


# -------------------------------
# Chunk text
# -------------------------------
def chunk_text(text, chunk_size=500):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks


# -------------------------------
# Convert text chunks to embeddings
# -------------------------------
def get_embeddings(chunks):
    embeddings = embedding_model.encode(chunks)
    return embeddings


# -------------------------------
# Store chunks in vector database
# -------------------------------
def store_chunks(chunks, embeddings):
    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        ids=ids
    )


# -------------------------------
# Retrieve relevant chunks
# -------------------------------
def retrieve(query):
    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    return results["documents"][0]


# -------------------------------
# Generate answer using Groq
# -------------------------------
def generate_answer(question):
    docs = retrieve(question)
    context = "\n".join(docs)

    prompt = f"""
    Answer only using the given context.
    Context:
    {context}
    Question:
    {question}
    """

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
