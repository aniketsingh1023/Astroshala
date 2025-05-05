from langchain_huggingface import HuggingFaceEmbeddings
from pymongo import MongoClient
from gridfs import GridFS
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name='thenlper/gte-large')

def generate_embedding(text):
    """Generate embedding vector for text"""
    return embedding_model.embed_query(text)

def connect_to_mongodb():
    """Connect to MongoDB and return client, db, GridFS, and collections"""
    # Get MongoDB connection details
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGODB_URI environment variable is not set")
        
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    
    # Get database
    db_name = os.getenv("MONGODB_DATABASE", "vector_db")
    db = client[db_name]
    
    # Initialize GridFS for file storage
    fs = GridFS(db, collection="pdfs")
    
    # Get collections
    pdf_collection = db["pdfs.files"]
    vector_collection = db[os.getenv("COLLECTION_NAME", "pdf_documents")]
    
    return client, db, fs, pdf_collection, vector_collection

def create_vector_store(texts):
    """Create a vector store from text chunks"""
    try:
        logger.info(f"Creating vector store with {len(texts)} text chunks")
        
        # Connect to MongoDB
        client, db, _, _, vector_collection = connect_to_mongodb()
        
        # Generate embeddings and store in MongoDB
        documents = []
        for i, text in enumerate(texts):
            try:
                # Generate embedding
                embedding = generate_embedding(text)
                
                # Create document
                document = {
                    "text": text,
                    "embedding": embedding,
                    "metadata": {"index": i}
                }
                
                documents.append(document)
                
                # Log progress
                if (i + 1) % 10 == 0 or i == len(texts) - 1:
                    logger.info(f"Processed {i + 1}/{len(texts)} documents")
                    
            except Exception as e:
                logger.error(f"Error embedding document {i}: {str(e)}")
        
        # Insert into MongoDB
        if documents:
            vector_collection.insert_many(documents)
            logger.info(f"Successfully inserted {len(documents)} documents into vector store")
            return True
        else:
            logger.warning("No documents to insert")
            return False
            
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        return False

def get_vector_store():
    """Get a vector store interface for similarity search"""
    try:
        # Connect to MongoDB
        client, db, _, _, vector_collection = connect_to_mongodb()
        
        # Check if the collection exists and has documents
        doc_count = vector_collection.count_documents({})
        if doc_count == 0:
            logger.error("No documents in the vector store")
            return None
            
        # Return a VectorStore object
        return MongoDBVectorStore(vector_collection)
        
    except Exception as e:
        logger.error(f"Error getting vector store: {str(e)}")
        return None

class MongoDBVectorStore:
    """Wrapper around MongoDB for vector search"""
    
    def __init__(self, collection):
        self.collection = collection
    
    def similarity_search(self, query, k=5):
        """Find similar documents to the query"""
        try:
            # Search for similar documents
            results = search_similar_pdfs(query, k)
            
            # Convert to the expected format
            documents = []
            for result in results:
                documents.append({
                    "page_content": result.get("text", ""),
                    "metadata": result.get("metadata", {})
                })
                
            return documents
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []

def search_similar_pdfs(query, top_k=5):
    try:
        # Connect to MongoDB
        client, db, _, _, vector_collection = connect_to_mongodb()
        
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Perform vector search using MongoDB Atlas
        try:
            results = vector_collection.aggregate([
                {
                    "$search": {
                        "index": os.getenv("VECTOR_INDEX_NAME", "vectorSearchIndex"),
                        "knnBeta": {
                            "vector": query_embedding,
                            "path": "embedding",
                            "k": top_k
                        }
                    }
                }
            ])
            
            result_list = list(results)
            if result_list:
                logger.info(f"Vector search found {len(result_list)} results")
                return result_list
            else:
                logger.info("Vector search returned no results, trying text search")
        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
        
        # Fall back to text search
        logger.info("Falling back to text search")
        results = vector_collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(top_k)
        
        return list(results)
    except Exception as e:
        logger.error(f"Error searching similar PDFs: {str(e)}")
        return []

def count_documents():
    """Count the number of documents in the vector store"""
    try:
        # Connect to MongoDB
        client, db, _, _, vector_collection = connect_to_mongodb()
        
        # Count documents
        count = vector_collection.count_documents({})
        return count
    except Exception as e:
        logger.error(f"Error counting documents: {str(e)}")
        return 0

def get_document_samples(limit=5):
    """Get a sample of documents from the vector store for inspection"""
    try:
        # Connect to MongoDB
        client, db, _, _, vector_collection = connect_to_mongodb()
        
        # Get samples
        samples = list(vector_collection.find({}, {"text": 1, "filename": 1}).limit(limit))
        return samples
    except Exception as e:
        logger.error(f"Error getting document samples: {str(e)}")
        return []

def store_pdfs_in_mongodb():
    """Store PDF chunks with embeddings in MongoDB, skipping already processed PDFs."""
    try:
        # Import here to avoid circular imports
        from rag.pdf_processor import load_and_split_pdfs
        import os
        
        # Connect to MongoDB
        client, db, fs, pdf_collection, _ = connect_to_mongodb()
        
        # Get existing PDF filenames in MongoDB
        existing_pdfs = set()
        for pdf_doc in pdf_collection.find({}, {"filename": 1}):
            if "filename" in pdf_doc:
                existing_pdfs.add(pdf_doc["filename"])
        
        logger.info(f"Found {len(existing_pdfs)} PDFs already in MongoDB")
        
        # Get list of PDFs in the directory
        pdf_dir = os.getenv("PDF_DIR", "../pdf_files")
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        
        # Filter out PDFs that are already processed
        new_pdfs = [pdf for pdf in pdf_files if pdf not in existing_pdfs]
        
        if not new_pdfs:
            logger.info("No new PDFs to process - all files already in MongoDB")
            return count_documents()
        
        logger.info(f"Found {len(new_pdfs)} new PDFs to process")
        
        # Process only new PDFs
        logger.info("Loading and splitting new PDFs...")
        report_chunks = load_and_split_pdfs(specific_files=new_pdfs)
        
        if not report_chunks or len(report_chunks) == 0:
            logger.warning("No valid content found in new PDFs")
            return count_documents()
        
        logger.info(f"Processing {len(report_chunks)} document chunks...")
        
        # Create vector store
        success = create_vector_store(report_chunks)
        
        if success:
            logger.info(f"✅ Successfully stored new document chunks in MongoDB!")
            # Count documents
            count = count_documents()
            return count
        else:
            logger.error("Failed to create vector store")
            return count_documents()
            
    except Exception as e:
        logger.error(f"Error storing PDFs in MongoDB: {str(e)}")
        return count_documents()

def test_vector_search():
    """Test the vector search functionality"""
    try:
        # Connect to MongoDB
        client, db, _, _, vector_collection = connect_to_mongodb()
        
        # Check if the collection exists and has documents
        doc_count = vector_collection.count_documents({})
        if doc_count == 0:
            logger.error("No documents in the vector store. Please process PDFs first.")
            return False
            
        # Check if the vector search index exists
        try:
            # Try a simple vector search
            test_query = "astrology"
            query_embedding = generate_embedding(test_query)
            
            results = vector_collection.aggregate([
                {
                    "$search": {
                        "index": os.getenv("VECTOR_INDEX_NAME", "vectorSearchIndex"),
                        "knnBeta": {
                            "vector": query_embedding,
                            "path": "embedding",
                            "k": 1
                        }
                    }
                },
                {"$limit": 1}
            ])
            
            # Try to get the first result
            list(results)
            logger.info("Vector search index is working")
            return True
            
        except Exception as e:
            logger.error(f"Vector search test failed: {e}")
            logger.error("You may need to create a vector search index in MongoDB Atlas")
            return False
            
    except Exception as e:
        logger.error(f"Error testing vector search: {str(e)}")
        return False

if __name__ == "__main__":
    print("\nVector Store Test")
    print("=" * 80)
    
    # Test MongoDB connection
    try:
        client, db, fs, pdf_collection, vector_collection = connect_to_mongodb()
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        import sys
        sys.exit(1)
        
    # Count documents
    doc_count = count_documents()
    print(f"Documents in vector store: {doc_count}")
    
    if doc_count > 0:
        # Test vector search
        if test_vector_search():
            print("✅ Vector search index is working")
        else:
            print("❌ Vector search index test failed")
            
        # Get sample documents
        samples = get_document_samples(2)
        if samples:
            print("\nSample documents:")
            for i, sample in enumerate(samples):
                text = sample.get('text', '')[:150] + '...' if len(sample.get('text', '')) > 150 else sample.get('text', '')
                print(f"[{i+1}] {sample.get('filename', 'Unknown')}: {text}")
    else:
        print("No documents in vector store. Please process PDFs first.")