import hnswlib
import uuid
from typing import List, Dict, Optional, Generator
import cohere
from unstructured.partition.html import partition_html
from unstructured.partition.text import partition_text
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean_extra_whitespace, group_broken_paragraphs
import io
import requests

class Documents:
    """Manages document loading, chunking, embedding, indexing, and retrieval."""

    def __init__(self, sources: List[Dict[str, str]], client: cohere.ClientV2):
        self.sources = sources
        self.co = client
        self.docs: List[Dict[str, str]] = []
        self.docs_embs: List[List[float]] = []
        self.retrieve_top_k = 20
        self.rerank_top_k = 5
        self.idx = None
        
        self.load()
        self.embed()
        self.index()

    def load(self) -> None:
        """Loads and chunks documents from sources."""
        print("Loading documents...")
        
        for source in self.sources:
            try:
                content = None
                content_type = ""
                url_lower = source["url"].lower()

                if source["url"].startswith("http"):
                    response = requests.get(source["url"], headers={"User-Agent": "Mozilla/5.0"})
                    response.raise_for_status()
                    content = response.content
                    content_type = response.headers.get("Content-Type", "")
                else:
                    try:
                        with open(source["url"], "rb") as f:
                            content = f.read()
                        if url_lower.endswith(".pdf"):
                            content_type = "application/pdf"
                        else:
                            content_type = "text/html"
                    except FileNotFoundError:
                        print(f"File not found: {source['url']}")
                        continue

                # Partition based on type
                if "application/pdf" in content_type or url_lower.endswith(".pdf"):
                    print(f"Processing PDF: {source['url']}")
                    # Use pdfminer with LAParams for better layout analysis
                    raw_text = extract_text(io.BytesIO(content), laparams=LAParams())
                    elements = partition_text(text=raw_text)
                else:
                    text_content = content.decode("utf-8", errors="ignore")
                    elements = partition_html(text=text_content, skip_headers_and_footers=True)
                
                # Chunking
                chunks = chunk_by_title(
                    elements,
                    max_characters=2000,
                    new_after_n_chars=1200,
                    combine_text_under_n_chars=250,
                    overlap=200
                )
                
                # Process chunks
                for chunk in chunks:
                    text = clean_extra_whitespace(group_broken_paragraphs(chunk.text))
                    
                    if not text.strip():
                        continue
                        
                    self.docs.append({
                        "title": source.get("title", "Untitled"),
                        "text": text,
                        "url": source["url"]
                    })
            except Exception as e:
                print(f"Error loading {source['url']}: {e}")

    def embed(self) -> None:
        """Embeds documents using Cohere."""
        print("Embedding documents...")
        if not self.docs:
            return

        batch_size = 90
        for i in range(0, len(self.docs), batch_size):
            batch = self.docs[i: i + batch_size]
            texts = [item["text"] for item in batch]
            try:
                response = self.co.embed(
                    texts=texts,
                    model="embed-english-v3.0",
                    input_type="search_document",
                    embedding_types=["float"]
                )
                if response.embeddings and response.embeddings.float_:
                    self.docs_embs.extend(response.embeddings.float_)
            except Exception as e:
                print(f"Error embedding batch: {e}")

    def index(self) -> None:
        """Indexes embeddings using HNSWLib."""
        print("Indexing documents...")
        if not self.docs_embs:
            return

        doc_count = len(self.docs_embs)
        dim = len(self.docs_embs[0]) 
        
        self.idx = hnswlib.Index(space="ip", dim=dim)
        self.idx.init_index(max_elements=doc_count, ef_construction=200, M=16)
        self.idx.add_items(self.docs_embs, list(range(doc_count)))
        print(f"Indexing complete: {doc_count} chunks")

    def retrieve(self, query: str) -> List[Dict[str, str]]:
        """Retrieves and reranks relevant documents."""
        if not self.idx or not self.docs:
            return []

        # Embed Query
        response = self.co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query",
            embedding_types=["float"]
        )
        query_emb = response.embeddings.float_[0]

        # KNN Search
        k_neighbors = min(self.retrieve_top_k, len(self.docs))
        doc_ids, _ = self.idx.knn_query(query_emb, k=k_neighbors)
        doc_ids = doc_ids[0]

        candidates = [self.docs[uid]["text"] for uid in doc_ids]
        candidate_ids = [uid for uid in doc_ids]

        # Rerank
        rerank_resp = self.co.rerank(
            query=query,
            documents=candidates,
            top_n=self.rerank_top_k,
            model="rerank-english-v3.0"
        )

        final_docs = []
        for result in rerank_resp.results:
            original_doc_idx = candidate_ids[result.index]
            doc = self.docs[original_doc_idx].copy()
            doc["score"] = result.relevance_score
            final_docs.append(doc)

        return final_docs


class Chatbot:
    """RAG Chatbot using Cohere V2."""

    def __init__(self, docs: Documents, client: cohere.ClientV2):
        self.docs = docs
        self.client = client
        self.conversation_id = str(uuid.uuid4())

    def generate_response(self, message: str) -> Generator[str, None, None]:
        print(f"Retrieving for query: {message}")
        retrieved_docs = self.docs.retrieve(message)
        
        formatted_docs = []
        for doc in retrieved_docs:
            formatted_docs.append({
                "data": {
                    "title": doc.get("title", ""),
                    "text": doc.get("text", ""),
                    "url": doc.get("url", "")
                }
            })

        try:
            stream = self.client.chat_stream(
                model="command-a-03-2025", 
                messages=[{"role": "user", "content": message}],
                documents=formatted_docs,
            )

            for event in stream:
                if event.type == "content-delta":
                    yield event.delta.message.content.text
                    
        except Exception as e:
            yield f"Error: {e}"
