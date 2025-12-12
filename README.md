# Local RAG Demo

This is a **Retrieval-Augmented Generation (RAG)** application that runs **completely locally** on your machine. It allows you to chat with your own documents (currently Markdown) using open-source AI models.

## 🚀 Features

*   **Privacy-First**: Everything runs offline. No data leaves your machine.
*   **Vector Database**: Uses **ChromaDB** to store and retrieve semantic information.
*   **Local Embeddings**: Uses `sentence-transformers/all-MiniLM-L6-v2` for fast and free embeddings.
*   **Local LLM**: Uses `google/flan-t5-base` (via Hugging Face) to generate answers based on your data.
*   **Custom Data**: Simply add `.md` files to the `data/` folder to expand the knowledge base.

## 🛠️ Tech Stack

*   **Python**: Core programming language.
*   **LangChain**: Framework for building the RAG pipeline.
*   **ChromaDB**: Vector store for document retrieval.
*   **HuggingFace Transformers**: For loading local LLM and embedding models.

## ⚙️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/TechSuvam/RAG_Demo.git
    cd RAG_Demo
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃 Usage

1.  **Add your Data**:
    Place any Markdown (`.md`) files you want to query inside the `data/` directory.

2.  **Run the Application**:
    ```bash
    python main.py
    ```

    *Note: The first run will download the AI models (~1GB total), which may take a few minutes.*

## 📂 Project Structure

```
RAG_Demo/
├── data/               # Knowledge base (add .md files here)
├── chroma_db/          # Persistent vector database storage
├── main.py             # Main RAG pipeline script
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## 📝 Example Output

```text
Query: 'What is RAG?'
Answer: Retrieval-Augmented Generation (RAG) is a technique for enhancing the accuracy and reliability of generative AI models...
```
