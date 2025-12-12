import os
import glob
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Load Markdown Files
def load_documents(directory):
    documents = []
    # Find all .md files in the directory
    md_files = glob.glob(os.path.join(directory, "*.md"))
    
    print(f"Found {len(md_files)} markdown files in {directory}...")
    
    for file_path in md_files:
        try:
            loader = UnstructuredMarkdownLoader(file_path)
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded: {file_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    return documents

# 2. Split Text into Chunks
def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    return text_splitter.split_documents(documents)

# 3. Initialize Vector DB and Embeddings
def create_vector_store(chunks):
    # Use HuggingFace embeddings (runs locally, no API key needed)
    print("Initializing embedding model (this may take a moment)...")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create Chroma Vector Store
    # persist_directory="./chroma_db" saves the DB to disk
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embedding_model,
        persist_directory="./chroma_db"
    )
    return vectorstore

def main():
    data_dir = "./data"
    
    # Make sure data dir exists
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} not found. Creating it...")
        os.makedirs(data_dir)
    
    # 1. Load
    docs = load_documents(data_dir)
    if not docs:
        print("No documents found. Please add .md files to the 'data' directory.")
        return

    # 2. Split
    chunks = split_documents(docs)
    print(f"Split {len(docs)} documents into {len(chunks)} chunks.")

    # 3. Store
    vectorstore = create_vector_store(chunks)
    print("Vector database created successfully.")

    # 4. Test Retrieval
    queries = ["What is RAG?", "What are the use cases of Python?"]
    
    for query in queries:
        print(f"\n{'='*40}")
        print(f"Test Query: '{query}'")
        print(f"{'='*40}")
        
        results = vectorstore.similarity_search(query, k=1)
        
        for i, res in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Source: {res.metadata.get('source', 'Unknown')}")
            print(f"Content Preview: {res.page_content[:300]}...\n")

if __name__ == "__main__":
    main()
