# AI Chatbot (Groq + RAG)

## Setup

1. **Get your Groq API key**
   - Go to https://console.groq.com
   - Create an account → API Keys → Create Key
   - Copy `.env.example` to `.env` and paste your key in as `GROQ_API_KEY`

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Usage

- **General Chat** — talk to the model (Llama 3.1 8B via Groq) directly
- **Chat with Documents** — drop PDFs into the `docs/` folder, click "Rebuild Knowledge Base", then ask questions about them

## Project Structure

```
chatbot/
  app.py           ← Streamlit UI
  rag.py           ← RAG + Groq logic
  requirements.txt
  .env.example     ← Template — copy to .env and fill in your key
  .env             ← Your API key (gitignored, never commit this)
  docs/            ← Drop your PDFs here
  chroma_db/       ← Auto-created vector store (gitignored)
```
