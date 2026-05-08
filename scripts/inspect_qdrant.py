from qdrant_client import QdrantClient

client = QdrantClient(path="./qdrant_storage")
collection_name = "destinations"

def inspect():
    count = client.count(collection_name=collection_name).count
    print(f"Points in collection: {count}")
    
    if count > 0:
        results = client.scroll(collection_name=collection_name, limit=10)
        for point in results[0]:
            print(f"ID: {point.id}, Payload: {point.payload}")

if __name__ == "__main__":
    inspect()
