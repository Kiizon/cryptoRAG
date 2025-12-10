from typing import List, Dict
from uuid import uuid4
import cohere

class Documents:
    """
    Class to store and retrieve documents using Cohere v2 embeddings for semantic search.
    """
    def __init__(self, sources: List[Dict[str, str]], client: cohere.ClientV2):
        self.sources = sources 
        self.client = client
        # Pre-compute embeddings for all documents
        texts = [doc.get("text", "") or doc.get("snippet", "") or doc.get("title", "") for doc in sources]
        if texts and any(texts):
            response = client.embed(
                texts=texts,
                model="embed-english-v3.0",
                input_type="search_document",
                embedding_types=["float"]
            )
            self.embeddings = response.embeddings.float_
        else:
            self.embeddings = []

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """
        Retrieve top_k most relevant documents using semantic similarity.
        """
        if not self.embeddings:
            return self.sources[:top_k]
            
        response = self.client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query",
            embedding_types=["float"]
        )
        query_embedding = response.embeddings.float_[0]
        
        # Compute cosine similarities
        similarities = [sum(q * d for q, d in zip(query_embedding, doc_emb)) for doc_emb in self.embeddings]
        
        # Get top_k indices
        top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        
        # Return documents
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
    Class representing a RAG chatbot using Cohere v2 API
    """
    def __init__(self, documents: Documents, client: cohere.ClientV2):
        self.docs = documents
        self.client = client
        self.conversation_history: List[Dict] = []

    def generate_response(self, prompt: str):
        # Retrieve relevant documents
        retrieved_docs = self.docs.retrieve(prompt, top_k=5)
        
        # Format documents for v2 API
        formatted_docs = []
        for doc in retrieved_docs:
            formatted_docs.append({
                "id": doc.get("id", ""),
                "data": {
                    "title": doc.get("title", ""),
                    "text": doc.get("text", "") or doc.get("snippet", "") or doc.get("url", "")
                }
            })
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Generate response with streaming using v2 API
        stream = self.client.chat_stream(
            model="command-r-plus",
            messages=self.conversation_history,
            documents=formatted_docs if formatted_docs else None
        )
        
        full_response = ""
        for event in stream:
            if event.type == "content-delta":
                text = event.delta.message.content.text
                full_response += text
                yield text
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant", 
            "content": full_response
        })
