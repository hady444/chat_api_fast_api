import os
import json
from pathlib import Path

import yaml
from loguru import logger
from opik import opik_context, track
from smolagents import Tool

from pinecone import Pinecone, ServerlessSpec

class PineconeRetrieverTool(Tool):
    name = "pinecone_vector_search_retriever"
    description = """Use this tool to search and retrieve relevant documents from a Pinecone vector database using semantic search."""

    inputs = {
        "query": {
            "type": "string",
            "description": """JSON string with a "query" field containing the user's search query."""
        }
    }
    output_type = "string"

    def __init__(self, config_path: Path, **kwargs):
        super().__init__(**kwargs)
        config = yaml.safe_load(config_path.read_text())["parameters"]
        
        # Initialize Pinecone with new API
        pinecone_api_key = os.getenv("PINECONE_API_KEY", config.get("pinecone_api_key"))
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        self.index_name = config["pinecone_index_name"]
        self.namespace = config.get("pinecone_namespace", "__default__")
        self.top_k = config.get("k", 5)
        
        # Check if index exists using new API
        existing_indexes = self.pc.list_indexes().names()
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=config["dimension"],
                metric=config.get("metric", "cosine"),
                spec=ServerlessSpec(
                    cloud=config.get("cloud", "aws"),
                    region=config.get("region", "us-east-1")
                )
            )
        
        # Get the index host
        index_info = self.pc.describe_index(self.index_name)
        self.index = self.pc.Index(host=index_info.host)

    @track(name="PineconeRetrieverTool.forward")
    def forward(self, query: str) -> str:
        opik_context.update_current_trace(
            tags=["agent"],
            metadata={
                "top_k": self.top_k,
                "index": self.index_name,
                "namespace": self.namespace
            }
        )
        try:
            q = json.loads(query)["query"]
            
            # Search using the new Pinecone API
            results = self.index.search(
                namespace=self.namespace,
                query={
                    "inputs": {"text": q},
                    "top_k": self.top_k
                },
                fields=["category", "original_text"]
            )
            
            formatted = []
            for i, hit in enumerate(results.get('result', {}).get('hits', []), start=1):
                # Extract the content from fields
                fields = hit.get('fields', {})
                content = fields.get('original_text', '')
                
                doc_id = hit.get('_id', '')
                url = 'No URL'
                title = 'Untitled'
                
                # Parse URL from _id if it starts with 'url_'
                if doc_id.startswith('url_'):
                    parts = doc_id.split('_chunk_')
                    if parts:
                        url_part = parts[0].replace('url_', '')
                        if url_part:
                            url = url_part
                            # Extract a simple title from URL (last part of path)
                            try:
                                title = url.split('/')[-1].replace('.html', '').replace('-', ' ').title()
                            except:
                                title = 'Document'
                
                # Get the relevance score
                score = hit.get('_score', 0)
                
                formatted.append(f"""
            <document id="{i}">
            <title>{title}</title>
            <url>{url}</url>
            <content>{content.strip()}</content>
            <score>{score:.4f}</score>
            </document>
            """)

            return "<search_results>\n" + "\n".join(formatted) + "\n</search_results>\n" + \
                "Include the <url> as a reference when quoting content."
                   
        except Exception as e:
            logger.opt(exception=True).debug("Error retrieving from Pinecone")
            return f"Error retrieving documents from Pinecone: {str(e)}"