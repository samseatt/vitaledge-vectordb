import faiss
import pickle
import numpy as np


def dump_faiss_index(index_path="./data/faiss_index", map_path="./data/faiss_index_text_map.pkl", sample_size=5):
    """
    Dump a condensed view of the FAISS index and its metadata.

    Args:
        index_path (str): Path to the FAISS index file.
        map_path (str): Path to the metadata mapping file.
        sample_size (int): Number of sample entries to display.

    Returns:
        None
    """
    try:
        # Load the FAISS index
        print(f"Reading FAISS index from: {index_path}")
        index = faiss.read_index(index_path)
        print(f"Loaded FAISS index: {type(index)}")
        print(f"Number of vectors stored: {index.ntotal}")
        
        # Check if index is wrapped
        if isinstance(index, faiss.IndexIDMap):
            print("Index is wrapped with IndexIDMap. Accessing the underlying index.")
            base_index = index.index
        else:
            base_index = index

        # Display dimensionality
        embedding_dim = base_index.d
        print(f"Dimensionality of vectors: {embedding_dim}")

        # Optionally, sample the stored vectors
        if base_index.ntotal > 0:
            vectors = np.zeros((base_index.ntotal, embedding_dim), dtype="float32")
            for i in range(min(sample_size, base_index.ntotal)):
                base_index.reconstruct(i, vectors[i])
            print(f"Sample stored vectors (showing {sample_size}):")
            print(vectors[:sample_size])

    except Exception as e:
        print(f"Error reading FAISS index: {e}")

    try:
        # Load the index-to-metadata map
        print(f"Reading metadata map from: {map_path}")
        with open(map_path, "rb") as f:
            metadata_map = pickle.load(f)
        print(f"Total IDs in metadata map: {len(metadata_map)}")
        
        # Display a sample of the metadata
        print(f"Sample metadata entries (showing {sample_size}):")
        for idx, (key, value) in enumerate(metadata_map.items()):
            if idx >= sample_size:
                break
            print(f"ID: {key}, Text: {value}")

    except Exception as e:
        print(f"Error reading metadata map: {e}")


# Example usage
dump_faiss_index()

