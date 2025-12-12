import streamlit as st
import os
import glob
from langchain_community.document_loaders import UnstructuredMarkdownLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Page Config
st.set_page_config(page_title="DocuMind", page_icon="🧠", layout="wide")

st.title("🧠 DocuMind")
st.markdown("Chat with your documents (Markdown & PDF) purely offline.")

# --- Backend Logic (Cached) ---

@st.cache_resource
def get_embedding_model():
    """Load the embedding model once."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

@st.cache_resource
def get_llm():
    """Load the LLM once."""
    return HuggingFacePipeline.from_model_id(
        model_id="google/flan-t5-base", 
        task="text2text-generation",
        pipeline_kwargs={"max_new_tokens": 200}
    )

def load_and_process_documents(directory):
    """Load documents from directory and update the vector store."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # Get all .md and .pdf files
    md_files = glob.glob(os.path.join(directory, "*.md"))
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    all_files = md_files + pdf_files
    
    if not all_files:
        st.warning("No Markdown or PDF files found in the 'data' directory.")
        return None

    documents = []
    status_text = st.empty()
    status_text.text(f"Found {len(all_files)} files. Loading...")
    
    for file_path in all_files:
        try:
            if file_path.endswith(".md"):
                loader = UnstructuredMarkdownLoader(file_path)
            elif file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            else:
                continue
                
            docs = loader.load()
            documents.extend(docs)
            status_text.text(f"Loaded: {os.path.basename(file_path)}")
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")

    if not documents:
        return None

    # Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    status_text.text(f"Split {len(documents)} docs into {len(chunks)} chunks.")

    # Embed and Store
    embedding_model = get_embedding_model()
    status_text.text("Updating Vector DB (this might take a second)...")
    
    # Simple persistence: delete old DB to avoid duplicates for this demo
    # In production, you'd add to it carefully.
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embedding_model,
        persist_directory="./chroma_db"
    )
    status_text.success("Knowledge Base Updated!")
    return vectorstore

def get_vectorstore():
    """Get the existing vectorstore."""
    embedding_model = get_embedding_model()
    if os.path.exists("./chroma_db"):
        return Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)
    return None

# --- UI Layout ---

with st.sidebar:
    st.header("Upload Data")
    uploaded_files = st.file_uploader("Upload PDF or MD files", type=["pdf", "md"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process Uploaded Files"):
            save_dir = "./data"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            with st.spinner("Saving files..."):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(save_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.success(f"Saved {len(uploaded_files)} files to {save_dir}")
            
            with st.spinner("Indexing..."):
                load_and_process_documents(save_dir)
                
    st.markdown("---")
    st.header("Settings")
    if st.button("Re-index Existing Data"):
        with st.spinner("Indexing..."):
            load_and_process_documents("./data")

    st.markdown("---")
    st.markdown("**Status:**")
    if os.path.exists("./chroma_db"):
        st.success("Vector DB Ready")
    else:
        st.error("Vector DB Missing. Click 'Re-index' or Upload files.")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about your docs..."):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Assistant Response
    with st.chat_message("assistant"):
        vectorstore = get_vectorstore()
        if not vectorstore:
            st.error("Please Index the Knowledge Base first!")
        else:
            with st.spinner("Thinking..."):
                try:
                    # Retrieve
                    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
                    docs = retriever.invoke(prompt)
                    
                    if not docs:
                        response = "I couldn't find any relevant information."
                    else:
                        context = "\n\n".join([doc.page_content for doc in docs])
                        llm = get_llm()
                        
                        # Generate
                        # T5 prompt structure that works better for valid QA
                        full_prompt = f"""Use the following pieces of context to answer the question at the end. 
If the answer is not in the context, just say that you don't know, don't try to make up an answer.
If the question is a greeting (like hello, hi), simply greet the user back.

Context:
{context}

Question: {prompt}

Helpful Answer:"""
                        response = llm.invoke(full_prompt)
                    
                    st.markdown(response)
                    
                    # Show Sources
                    with st.expander("View Sources"):
                        for doc in docs:
                            st.markdown(f"**Source:** {doc.metadata.get('source', 'Unknown')}")
                            st.caption(doc.page_content[:300] + "...")

                    # Save History
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    st.error(f"An error occurred: {e}")
