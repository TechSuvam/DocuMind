# 📘 DocuMind: Detailed Project Explanation

This document explains **exactly how this project works**, from the high-level concept to the specific code implementation.

---

## 1. What is this project?
This is a **Local RAG (Retrieval-Augmented Generation) Application**.
*   **"Local"**: It runs entire on your computer (or server). No data is sent to OpenAI, Google, or any cloud API.
*   **"RAG"**: It combines a search engine ("Retrieval") with a creative AI ("Generation").

**The Goal**: To chat with your own private documents (PDFs, Markdown) that the AI wasn't trained on originally.

---

## 2. Architecture: How it works under the hood

The system follows a 4-step pipeline:

### Step 1: Ingestion (Loading Data)
*   **What it does**: Reads your files (`.pdf`, `.md`) from the `data/` folder.
*   **Library Used**: `langchain`, `pypdf`, `unstructured`.
*   **Code**: `load_and_process_documents()` in `app.py`.
*   **Why**: Computers can't read "files" directly; they need raw text. We strip images/formatting and just keep the text.

### Step 2: Splitting (Chunking)
*   **What it does**: breaks huge documents into small "chunks" (e.g., 1000 characters each).
*   **Library Used**: `RecursiveCharacterTextSplitter`.
*   **Why**: AI models have a memory limit (context window). You can't feed a 500-page book into it at once. We feed it small, relevant pieces.

### Step 3: Embeddings & Vector Storage
*   **What it does**: Converts text chunks into **Numbers** (Vectors) and saves them.
*   **Model Used**: `sentence-transformers/all-MiniLM-L6-v2`.
*   **Database**: `ChromaDB` (saved locally in `chroma_db/` folder).
*   **The Magic**: 
    *   Text: "The apple is red."
    *   Vector: `[0.12, 0.98, -0.05, ...]`
    *   Why? Because mathematically, the vector for "Apple" is close to the vector for "Fruit". This allows **Semantic Search** (searching by meaning, not just keywords).

### Step 4: Retrieval & Generation (The "Chat")
When you ask a question (e.g., *"What is Python?"*):
1.  **Retrieve**: The system converts your question into numbers. It asks ChromaDB: *"Give me the 2 chunks of text that are mathematically closest to this question."*
2.  **Augment**: We take those 2 chunks and paste them into a prompt for the AI.
    *   *Prompt*: "Use this context: [Chunk 1 text] [Chunk 2 text]. Answer this question: What is Python?"
3.  **Generate**: The AI model (`google/flan-t5-base`) reads the prompt and writes the answer.

---

## 3. Key Components (The Code)

### `app.py` (The User Interface)
This is the main entry point.
*   **`st.file_uploader`**: Handles PDF uploads.
*   **`@st.cache_resource`**: A performance trick. It loads the heavy AI models into memory *once* so the app doesn't freeze every time you click a button.
*   **`get_llm()`**: Downloads and runs the `flan-t5` model from HuggingFace.

### `Dockerfile` (Deployment)
This is a recipe for building a "virtual computer" (Container) that runs your app.
*   `FROM python:3.10-slim`: Starts with a lightweight Linux.
*   `RUN pip install ...`: Installs your libraries.
*   `CMD`: Tells it to launch Streamlit.
*   **Benefit**: This guarantees the app runs on AWS exactly how it runs on your laptop.

---

## 4. Why did we choose these technologies?
*   **LangChain**: The standard framework for gluing AI components together.
*   **ChromaDB**: The most popular open-source, local vector database. Zero setup required.
*   **Flan-T5**: A Google model that is **Open Source** and **Small** enough to run on a standard CPU without a GPU. (Larger models like Llama-3 would require a powerful NVIDIA card).

## 5. Limitations & Future Improvements
1.  **Model Intelligence**: `flan-t5-base` is small/smart "enough". For deeper reasoning, you'd upgrade to `Llama-3` or `Mistral` (requires more RAM/GPU).
2.  **Persistence**: Currently, if you delete `chroma_db`, the memory is lost. In production, you'd backup this folder.
3.  **Speed**: It runs on CPU. Using a GPU (via CUDA) would make answers instant.
