import os
import sys
import logging
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS

logger = logging.getLogger(__name__)


def load_documents(uploaded_files):
    """Load documents from Streamlit uploaded file objects (PDF, TXT, DOCX)"""
    from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader

    all_docs = []
    for f in uploaded_files:
        try:
            suffix = os.path.splitext(f.name)[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(f.read())
                tmp_path = tmp.name

            if suffix == ".pdf":
                loader = PyPDFLoader(tmp_path)
            elif suffix in (".txt", ".md"):
                loader = TextLoader(tmp_path, encoding="utf-8")
            elif suffix in (".docx", ".doc"):
                loader = Docx2txtLoader(tmp_path)
            else:
                logger.warning(f"Unsupported file type: {f.name}")
                os.unlink(tmp_path)
                continue

            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = f.name
            all_docs.extend(docs)
            os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"Error loading {f.name}: {e}")

    return all_docs


def split_documents(documents):
    """Split documents into overlapping chunks for embedding"""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        return splitter.split_documents(documents)
    except Exception as e:
        logger.error(f"Error splitting documents: {e}")
        return documents


def build_vector_store(chunks, embedding_model):
    """Build FAISS vector store from document chunks"""
    try:
        from langchain_community.vectorstores import FAISS
        return FAISS.from_documents(chunks, embedding_model)
    except Exception as e:
        logger.error(f"Error building vector store: {e}")
        return None


def retrieve_context(vector_store, query):
    """Retrieve relevant document chunks for a query"""
    try:
        results = vector_store.similarity_search(query, k=TOP_K_RESULTS)
        if not results:
            return ""
        parts = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source_file", "Unknown")
            parts.append(f"[Source {i}: {source}]\n{doc.page_content.strip()}")
        return "\n\n---\n\n".join(parts)
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return ""
