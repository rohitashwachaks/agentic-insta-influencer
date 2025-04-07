from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    ig_username: str
    ig_password: str
    elevenlabs_api_key: str
    data_dir: str = "./data"
    qdrant_url: str = "localhost"
    qdrant_port: int = 6333
    pinecone_api_key: str
    pinecone_region: str
    clip_index_name: str = "clip-index"
    phash_index_name: str = "phash-index"
    clip_dim: int = 512
    phash_dim: int = 64
    metric: str = "cosine"

    class Config:
        env_file = ".env"
