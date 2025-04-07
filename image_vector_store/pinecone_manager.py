from pinecone import Pinecone, ServerlessSpec

from utils.config import Settings

settings = Settings()


class PineconeManager:
    def __init__(self):
        self._pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
        self.clip_index = self._init_index(settings.clip_index_name, settings.clip_dim)
        self.phash_index = self._init_index(settings.phash_index_name, settings.phash_dim)

    def _init_index(self, name: str, dim: int):
        existing_indices = {t.name for t in self._pinecone_client.list_indexes()}
        if name not in existing_indices:
            self._pinecone_client.create_index(
                name,
                vector_type='dense',
                dimension=dim,
                metric=settings.metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.pinecone_region
                ),
            )
        return self._pinecone_client.Index(name)

    def get_index(self, index_type: str):
        if index_type == "clip":
            return self.clip_index
        elif index_type == "phash":
            return self.phash_index
        else:
            raise ValueError("Index type must be either 'clip' or 'phash'")