from typing import List, Dict
from uuid import uuid4
import cohere

class Documents:
    """
    Class to store and retrieve documents using Cohere embeddings for semantic search.
    """
    def __init__(self, sources: List[Dict[str, str]], client: cohere.Client):
        self.sources = sources 
        self.client = client
        # pre-compute embeddings
        texts = [doc.get("text", "") or doc.get("snippet", "") for doc in sources]
        self.embeddings = client.embed(texts=texts, model="embed-english-v3.0").embeddings

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """
        Retrieve top_k most relevant documents using semantic similarity.
        """
        query_embedding = self.client.embed(texts=[query], model="embed-english-v3.0").embeddings[0]
        
        # Compute cosine similarities (simple dot product since embeddings are normalized)
        similarities = [sum(q * d for q, d in zip(query_embedding, doc_emb)) for doc_emb in self.embeddings]
        
        # Get top_k indices
        top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        
        # Return documents in Cohere's expected format for RAG (dicts with string keys/values)
        retrieved = []
        for idx in top_indices:
            doc = self.sources[idx].copy()
            doc["id"] = str(idx)
            retrieved.append(doc)
        return retrieved

    def get_client(self):
        return self.client

class ChatBot:
    """
    Class representing a RAG chatbot using Cohere
    """
    def __init__(self, documents: Documents, client: cohere.Client):
        self.docs = documents
        self.client = client
        self.conversation_id = str(uuid4())

    def generate_response(self, prompt: str):
        # Step 1: Generate search queries
        response = self.client.chat(message=prompt, search_queries_only=True)
        
        if response.search_queries:
            print("Retrieving relevant information...")
            documents = self.get_docs(response)
        else:
            documents = []

        # Step 2: Generate grounded response with retrieved documents
        stream = self.client.chat(
            message=prompt,
            documents=documents,
            conversation_id=self.conversation_id,
            stream=True,
        )
        
        for event in stream:
            if hasattr(event, "event_type") and event.event_type == "text-generation":  # SDK may vary
                yield event.text
            elif hasattr(event, "text"):  # Alternative attribute in some SDK versions
                yield event.text

    def get_docs(self, response):
        """
        Extract queries and retrieve documents
        """
        queries = [sq.text for sq in response.search_queries] if response.search_queries else []
        retrieved_docs = []
        for query in queries:
            retrieved_docs.extend(self.docs.retrieve(query, top_k=5))
        return retrieved_docs