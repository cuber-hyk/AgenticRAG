import logging
from typing import List, Dict
from llama_index.core import Settings as LlamaSettings
from ..config import Settings

try:
    import weaviate
    from weaviate.auth import AuthApiKey
    from weaviate.classes.config import Property, DataType, Configure
except Exception:
    try:
        # Fallback for older versions or different structure
        import weaviate
        from weaviate.classes.init import AuthApiKey
        from weaviate.classes.config import Property, DataType, Configure
    except Exception:
        weaviate = None

logger = logging.getLogger(__name__)
_vs = None
_settings = Settings()


class VectorStore:
    def __init__(self, client, class_name: str):
        self.client = client
        self.class_name = class_name

    def recreate_schema(self):
        if self.client is None:
            return
        try:
            if self.client.collections.exists(self.class_name):
                self.client.collections.delete(self.class_name)
            self.client.collections.create(
                self.class_name,
                # Use none for now if inference service is missing, or user needs to start docker compose
                vectorizer_config=Configure.Vectorizer.none(),
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                ],
            )
        except Exception as e:
            logger.warning(f"failed to recreate schema: {e}")

    def upsert_documents(self, docs: List[Dict]):
        if self.client is None:
            return
        
        # Generate embeddings if model is available
        vectors = []
        if LlamaSettings.embed_model:
            try:
                texts = [d["text"] for d in docs]
                # Use batch embedding generation
                vectors = LlamaSettings.embed_model.get_text_embedding_batch(texts)
            except Exception as e:
                logger.error(f"Failed to generate embeddings: {e}")
        
        coll = self.client.collections.get(self.class_name)
        # Use batch insertion for efficiency
        with self.client.batch.dynamic() as batch:
            for i, d in enumerate(docs):
                vec = vectors[i] if i < len(vectors) else None
                batch.add_object(
                    properties={"text": d["text"], "source": d.get("source", "")},
                    vector=vec,
                    collection=self.class_name
                )
                # Fallback to single insert if batch fails? No, batch handles it usually.
                # If using loop:
                # coll.data.insert({"text": d["text"], "source": d.get("source", "")}, vector=vec)

    def query(self, query: str, top_k: int) -> List[Dict]:
        if self.client is None:
            return []
        coll = self.client.collections.get(self.class_name)
        try:
            if LlamaSettings.embed_model:
                query_vec = LlamaSettings.embed_model.get_query_embedding(query)
                res = coll.query.near_vector(near_vector=query_vec, limit=top_k)
            else:
                res = coll.query.near_text(query=query, limit=top_k)
        except Exception as e:
            # Fallback to BM25 if vector search failed
            logger.warning(f"Vector search failed, falling back to BM25: {e}")
            res = coll.query.bm25(query=query, limit=top_k)
            
        items = []
        for o in res.objects:
            props = o.properties
            items.append({"text": props.get("text", ""), "source": props.get("source", "")})
        return items


def get_vector_store() -> VectorStore:
    global _vs
    if _vs:
        return _vs
    client = None
    if weaviate:
        try:
            # Weaviate v4 client connection logic
            # For v4, WeaviateClient is internal, use connect_to_local or connect_to_custom
            if "localhost" in _settings.weaviate_url:
                 client = weaviate.connect_to_local(
                    port=8080,
                    grpc_port=50051,
                 )
            else:
                auth = AuthApiKey(_settings.weaviate_api_key) if _settings.weaviate_api_key else None
                client = weaviate.connect_to_custom(
                    http_host=_settings.weaviate_url.replace("http://", "").replace("https://", ""),
                    http_port=443 if _settings.weaviate_url.startswith("https") else 80,
                    http_secure=_settings.weaviate_url.startswith("https"),
                    auth_credentials=auth,
                    skip_init_checks=True,
                )
        except Exception as e:
            logger.warning(f"weaviate client init failed: {e}")
            # Fallback for some v3/v4 hybrid scenarios or different connection patterns
            try:
                auth = AuthApiKey(_settings.weaviate_api_key) if _settings.weaviate_api_key else None
                client = weaviate.WeaviateClient(
                    connection_params=None, # Not standard v4 way but let's try to avoid direct instantiation errors
                    auth_client_secret=auth
                )
            except:
                pass

    _vs = VectorStore(client, _settings.weaviate_class)
    return _vs
