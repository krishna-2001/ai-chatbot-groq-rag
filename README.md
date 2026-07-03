# AI Chatbot (Groq + RAG)

A Streamlit chatbot with two modes: general chat with an LLM, and a RAG (retrieval-augmented generation) mode that answers questions from your own PDFs.

All the code lives in the [`chatbot/`](./chatbot) folder.

## Setup

1. **Get your Groq API key**
   - Go to https://console.groq.com
   - Create an account → API Keys → Create Key
   - Inside `chatbot/`, copy `.env.example` to `.env` and paste your key in as `GROQ_API_KEY`

2. **Install dependencies**
   ```bash
   cd chatbot
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Usage

- **General Chat** — talk to the model (Llama 3.1 8B via Groq) directly
- **Chat with Documents** — drop PDFs into `chatbot/docs/`, click "Rebuild Knowledge Base" in the sidebar, then ask questions about them

## How the RAG pipeline works

PDFs are chunked with LangChain's text splitter, embedded with a sentence-transformers model, and stored in a local ChromaDB vector store. On each question, the top-k most relevant chunks are retrieved and passed to the model as context — if the answer isn't in the retrieved context, the model says so rather than guessing.

## Project Structure

```
chatbot/
  app.py           ← Streamlit UI
  rag.py           ← RAG + Groq logic
  requirements.txt
  .env.example     ← Template — copy to .env and fill in your key
  docs/            ← Drop your PDFs here
```

## Tech Stack

Python, Streamlit, LangChain, ChromaDB, sentence-transformers, Groq API (Llama 3.1 8B)
