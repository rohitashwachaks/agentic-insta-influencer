import os
from typing import List

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models


class QDrantDBClient:
    """
    A simple client to interact with Qdrant for storing and retrieving embeddings.
    """

    def __init__(self, host, port,
                 collection_name: str,
                 vectors_config: models.VectorParams,
                 overwrite: bool = False):
        """
        Initialize the Qdrant client.

        Args:
            host (str): The host of the Qdrant instance.
            port (int): The port of the Qdrant instance.
        """
        # host = os.environ.get("QDRANT_URL", 'localhost') if host is None else host
        # port = int(os.environ.get("QDRANT_PORT", 6333)) if port is None else port
        assert isinstance(host, str), "Host must be a string."
        assert isinstance(port, int), "Port must be an integer."
        assert port > 0, "Port must be a positive integer."

        self.collection_name = collection_name
        self.vectors_config = vectors_config
        self.client = QdrantClient(host=host, port=port)

        # Create the collection if it doesn't exist
        self.create_collection(overwrite)

    def create_collection(self, overwrite: bool = False):
        """
        Recreate a collection in Qdrant with the specified vector configuration.

        Args:
            collection_name (str): The name of the collection to create.
            vectors_config (models.VectorParams): The vector configuration for the collection.
            :param vectors_config:
            :param collection_name:
            :param overwrite:
        """
        if self.client.collection_exists(self.collection_name):  # Check if the collection exist
            print(f"Collection '{self.collection_name}' already exists.")
            if overwrite is True:
                print(f"OVERWRITE ENABLED. Purging collection '{self.collection_name}'.")
                self.client.delete_collection(self.collection_name)  # Delete the existing collection
            else:
                return

        # Create a new collection with the specified vector configuration
        print(f"Creating collection '{self.collection_name}' ...")
        self.client.create_collection(self.collection_name, self.vectors_config)
        print(f"Collection '{self.collection_name}' created successfully.")

    def upsert(self, points: List[models.PointStruct]):
        """
        Upsert points into a specified collection.

        Args:
            points (list): A list of PointStruct objects to upsert.
        """
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query: np.ndarray, limit: int):
        """
        Search for similar embeddings in a specified collection.

        Args:
            collection_name (str): The name of the collection to search in.
            query_vector (list): The query vector for searching.
            limit (int): The maximum number of results to return.

        Returns:
            list: A list of search results.
        """
        return self.client.query_points(collection_name=self.collection_name, query=query, limit=limit)

    def delete(self, points_selector: models.Filter):
        """
        Delete points from a specified collection.

        Args:
            collection_name (str): The name of the collection to delete points from.
            points_selector (models.Filter): A filter specifying which points to delete.
        """
        self.client.delete(collection_name=self.collection_name, points_selector=points_selector)


vector_db_client = QDrantDBClient()

# if __name__ == "__main__":
#     # Connect to the local Qdrant instance
#     # Create a collection with a specific vector size (e.g., 512)
#     client = QDrantDBClient(host="localhost", port=6333,
#                             collection_name="my_embeddings",
#                             vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
#                             overwrite=False)
#
#     vector_size = 512
#
#     # Example: Upsert an embedding with a custom ID
#     embedding = [0.1] * vector_size  # Replace with your actual embedding
#     client.upsert(
#         points=[
#             models.PointStruct(
#                 id=i,
#                 vector=[i] * vector_size,
#                 payload={"filename": f"image{i}.jpg"}
#             )
#             for i in range(50)
#         ]
#     )
#
#     # Example: Search for similar embeddings
#     query_vector = [0.1] * vector_size
#     search_result = client.search(
#         query=query_vector,
#         limit=5
#     )
#     print("Search result:", search_result)
#
#     # Example: Delete a vector by its ID
#     client.delete(
#         points_selector=models.Filter(ids=[1])
#     )
