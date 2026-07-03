import os
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from groq import Groq

load_dotenv()

DOCS_DIR = "docs"
CHROMA_DIR = "chroma_db"
MODEL = "llama-3.1-8b-instant"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_documents():
    """Load all PDFs from the docs/ folder."""
    texts = []
    if not os.path.isdir(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)
        return texts

    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".pdf"):
            try:
                reader = PdfReader(os.path.join(DOCS_DIR, filename))
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        texts.append(text)
            except Exception as e:
                print(f"Skipping {filename}: could not read PDF ({e})")
    return texts


def build_vectorstore():
    """Chunk docs and store embeddings in ChromaDB."""
    raw_texts = load_documents()
    if not raw_texts:
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.create_documents(raw_texts)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        chunks, embeddings, persist_directory=CHROMA_DIR
    )
    return vectorstore


def get_vectorstore():
    """Load existing ChromaDB or build a new one."""
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    if os.path.exists(CHROMA_DIR):
        return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    return build_vectorstore()


def rag_query(question: str) -> str:
    """Retrieve relevant chunks and answer using Claude."""
    vectorstore = get_vectorstore()
    if vectorstore is None:
        return "No documents found. Please add PDFs to the docs/ folder."

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use the provided context to answer questions accurately.",
                },
                {
                    "role": "user",
                    "content": f"""Use the following context to answer the question.
If the answer is not in the context, say so clearly.

Context:
{context}

Question: {question}""",
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, something went wrong calling the model: {e}"


def general_chat(messages: list) -> str:
    """Send a conversation to Groq (Llama3) and get a reply."""
    groq_messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    groq_messages.extend(messages)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=groq_messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, something went wrong calling the model: {e}"
