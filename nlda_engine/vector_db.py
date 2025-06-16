"""
The Vector Database for the Nalanda Engine.
Handles the creation, storage, and retrieval of text embeddings,
forming the core of the Retrieval-Augmented Generation (RAG) pipeline.
"""
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDB:
    """
    A simple vector database using FAISS and SentenceTransformers.
    """
    def __init__(self, corpus_dir='corpus/', model_name='all-MiniLM-L6-v2'):
        print("[VectorDB] Initializing...")
        self.corpus_dir = corpus_dir
        self.documents = []
        self.chunks = []
        
        try:
            self.embedding_model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"Error loading SentenceTransformer model: {e}")
            print("Please ensure you have a working internet connection to download the model.")
            self.embedding_model = None
            return

        self.index = None
        self._build_index()
        print(f"[VectorDB] Initialization complete. Indexed {len(self.chunks)} chunks from {len(self.documents)} documents.")

    def _load_documents(self):
        """Loads all .txt files from the corpus directory."""
        print(f"[VectorDB] Loading documents from '{self.corpus_dir}'...")
        for filename in os.listdir(self.corpus_dir):
            if filename.endswith(".txt"):
                with open(os.path.join(self.corpus_dir, filename), 'r') as f:
                    self.documents.append({"name": filename, "content": f.read()})

    def _chunk_documents(self):
        """Splits documents into smaller chunks (paragraphs in this case)."""
        print("[VectorDB] Chunking documents...")
        for doc in self.documents:
            # Simple chunking by splitting on double newlines
            paragraphs = doc['content'].strip().split('\\n\\n')
            for para in paragraphs:
                if para.strip(): # Ignore empty paragraphs
                    self.chunks.append(para)

    def _build_index(self):
        """Builds the FAISS index from the document chunks."""
        if not self.embedding_model:
            return
            
        self._load_documents()
        self._chunk_documents()
        
        if not self.chunks:
            print("[VectorDB] No document chunks to index.")
            return

        print("[VectorDB] Generating embeddings for chunks...")
        # Encode the chunks into vectors
        embeddings = self.embedding_model.encode(self.chunks, convert_to_tensor=False)
        
        # Build the FAISS index
        embedding_dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.index.add(np.array(embeddings).astype('float32'))
        print("[VectorDB] FAISS index built successfully.")

    def search(self, query: str, k: int = 3) -> list[str]:
        """
        Searches the index for the most relevant chunks to a query.
        
        Args:
            query (str): The search query.
            k (int): The number of top results to return.

        Returns:
            list[str]: A list of the most relevant text chunks.
        """
        if not self.index or not self.embedding_model:
            print("[VectorDB] Index or embedding model is not available.")
            return []

        # Encode the query and search the index
        query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        # Return the corresponding text chunks
        return [self.chunks[i] for i in indices[0]]

if __name__ == '__main__':
    # Example usage for testing
    db = VectorDB()
    if db.index:
        query = "What are the properties of a porcelain doll?"
        results = db.search(query, k=2)
        
        print(f"\\n--- Search results for: '{query}' ---")
        for i, res in enumerate(results):
            print(f"Result {i+1}:\\n{res}\\n" + "-"*20)

        query = "Tell me about granite."
        results = db.search(query, k=2)
        
        print(f"\\n--- Search results for: '{query}' ---")
        for i, res in enumerate(results):
            print(f"Result {i+1}:\\n{res}\\n" + "-"*20)
    else:
        print("Could not run tests because VectorDB failed to initialize.") 