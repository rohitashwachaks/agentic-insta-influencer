import uuid
from multiprocessing import Pool, cpu_count
from typing import List

from PIL import Image
from numpy import ndarray

from image_vector_store.image_embedder import ImageEmbedder
from image_vector_store.pinecone_manager import PineconeManager


def _vector_to_hash(phash_vec: List[float]) -> int:
    return int("".join(str(int(b)) for b in phash_vec), 2)


def _hamming_distance(a: int, b: int) -> int:
    return bin(a ^ b).count('1')


def _process_image(image_path: str):
    embedder = ImageEmbedder()
    try:
        image = Image.open(image_path).convert("RGB")
        clip_vector: ndarray = embedder.generate_clip_embedding(image)
        clip_vector: List[float] = clip_vector.tolist()
        phash_vector: List[float] = embedder.generate_phash_vector(image)
        phash_int = _vector_to_hash(phash_vector)
        return {
            "id": str(uuid.uuid4()),
            "clip": clip_vector,
            "phash": [float(x) for x in phash_vector],
            "phash_int": phash_int,
            "metadata": {
                "path": str(image_path),
                "phash_int": str(phash_int)  # Store as string to avoid JSON issues
            }
        }
    except Exception as e:
        print(f"[Error] {image_path}: {e}")
        return None


class VectorStore:
    def __init__(self):
        self.pinecone = PineconeManager()
        self.embedder = ImageEmbedder()

    def _is_duplicate(self, phash_int: int, phash_vector: List[int], threshold: int = 5, top_k: int = 5) -> bool:
        try:
            results = self.pinecone.phash_index.query(
                vector=phash_vector,
                top_k=top_k,
                include_metadata=True  # Only metadata needed
            )
            for match in results['matches']:
                match_hash_str = match['metadata'].get("phash_int")
                if not match_hash_str:
                    continue
                match_hash_int = int(match_hash_str)
                distance = _hamming_distance(phash_int, match_hash_int)
                if distance <= threshold:
                    return True
        except Exception as e:
            print(f"[Dedup Error] {e}")
        return False

    def upsert_batch(self, image_paths: List[str], batch_size: int = 100, hamming_threshold: int = 5):
        with Pool(processes=cpu_count()) as pool:
            results = pool.map(_process_image, image_paths)

        valid_data = []
        for item in results:
            if not item:
                continue
            if self._is_duplicate(item['phash_int'], item['phash'], threshold=hamming_threshold):
                print(f"[Duplicate] Skipped {item['metadata']['path']}")
                continue
            valid_data.append(item)

        ids_uploaded = []
        for i in range(0, len(valid_data), batch_size):
            batch = valid_data[i:i + batch_size]

            self.pinecone.clip_index.upsert([
                {
                    "id": item["id"],
                    "values": item["clip"],
                    "metadata": item["metadata"]
                } for item in batch
            ])

            self.pinecone.phash_index.upsert([
                {
                    "id": item["id"],
                    "values": item["phash"],
                    "metadata": item["metadata"]
                } for item in batch
            ])

            ids_uploaded.extend([item["id"] for item in batch])

        print(f"[Success] Uploaded {len(ids_uploaded)} unique images.")
        return ids_uploaded

    def find_duplicates(self, image_path: str, top_k: int = 3):
        image = Image.open(image_path).convert("RGB")
        phash_vector = self.embedder.generate_phash_vector(image)

        results = self.pinecone.phash_index.query(
            vector=phash_vector,
            top_k=top_k,
            include_metadata=True
        )
        return results["matches"]

    def search_similar(self, image_path: str, top_k: int = 5):
        image = Image.open(image_path).convert("RGB")
        clip_vector = self.embedder.generate_clip_embedding(image)

        results = self.pinecone.clip_index.query(
            vector=clip_vector,
            top_k=top_k,
            include_metadata=True
        )
        return results["matches"]
