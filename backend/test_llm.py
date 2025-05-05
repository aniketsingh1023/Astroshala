# init_rag.py
"""
Initialization script for the RAG model.
Run this script to ensure the PDF documents are properly processed and vectorized.
"""
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import settings
from rag.settings import PDF_DIR, DB_DIR

def initialize_rag(specific_files=None):
    """
    Initialize the RAG model by processing PDFs and creating vector embeddings
    
    Args:
        specific_files (list): Optional list of specific PDF filenames to process
    """
    try:
        # Import here to avoid circular imports
        from rag.pdf_processor import load_and_split_pdfs
        from rag.vector_store import store_pdfs_in_mongodb
        
        # Check if MongoDB connection is working
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            logger.error("MONGODB_URI environment variable is not set")
            return False
            
        try:
            client = MongoClient(mongo_uri)
            client.admin.command('ping')
            logger.info("MongoDB connection successful")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            return False
            
        # Check if the vector collection already exists and has documents
        db_name = os.getenv("MONGODB_DATABASE", "vector_db")
        collection_name = os.getenv("COLLECTION_NAME", "pdf_documents")
        
        db = client[db_name]
        collection = db[collection_name]
        
        doc_count = collection.count_documents({})
        logger.info(f"Found {doc_count} documents in the vector store")
        
        if doc_count > 0 and not specific_files:
            user_input = input(f"Found {doc_count} existing documents. Do you want to reprocess PDFs? (y/n): ")
            if user_input.lower() != 'y':
                logger.info("Skipping PDF processing as vector store already exists")
                return True
                
        # Process PDFs and create vector embeddings
        logger.info("Starting PDF processing...")
        
        # Check if PDF directory exists
        if not os.path.exists(PDF_DIR):
            logger.error(f"PDF directory not found: {PDF_DIR}")
            return False
            
        logger.info(f"Using PDF directory: {PDF_DIR}")
        
        # If specific files are provided, use them
        if specific_files:
            logger.info(f"Processing specific files: {', '.join(specific_files)}")
            # Store PDFs in MongoDB with vector embeddings
            try:
                # Import required modules and load the specified PDF files
                from rag.pdf_processor import load_and_split_pdfs
                from rag.vector_store import store_pdfs_in_mongodb
                
                # Adjust the function to accept specific files
                report_chunks = load_and_split_pdfs(specific_files=specific_files)
                if report_chunks:
                    num_documents = store_pdfs_in_mongodb(report_chunks)
                    logger.info(f"Successfully processed {num_documents} document chunks")
                    return True
                else:
                    logger.error("No document chunks generated from the specified files")
                    return False
            except Exception as e:
                logger.error(f"Error processing specified files: {str(e)}")
                return False
        else:
            # Count PDF files
            pdf_count = sum(1 for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf'))
            logger.info(f"Found {pdf_count} PDF files in {PDF_DIR}")
            
            if pdf_count == 0:
                # Try checking subdirectories
                total_pdfs = 0
                for root, dirs, files in os.walk(PDF_DIR):
                    for f in files:
                        if f.lower().endswith('.pdf'):
                            total_pdfs += 1
                            logger.info(f"Found PDF in subdirectory: {os.path.join(root, f)}")
                
                if total_pdfs == 0:
                    logger.error("No PDF files found. Please add PDFs to the specified directory")
                    return False
                else:
                    logger.info(f"Found {total_pdfs} PDF files in subdirectories")
            
            # Store PDFs in MongoDB with vector embeddings using default behavior
            num_documents = store_pdfs_in_mongodb()
            
            if num_documents > 0:
                logger.info(f"Successfully processed {num_documents} document chunks")
                return True
            else:
                logger.error("Failed to process documents")
                return False
            
    except Exception as e:
        logger.error(f"Error initializing RAG model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_rag_query():
    """Test the RAG model with a sample query"""
    try:
        # Import here to avoid circular imports
        from rag.vector_store import search_similar_pdfs, connect_to_mongodb
        
        # Check MongoDB connection and collection directly
        client, db, _, _, vector_collection = connect_to_mongodb()
        doc_count = vector_collection.count_documents({})
        logger.info(f"Vector collection contains {doc_count} documents")
        
        # Check if vector search index exists
        try:
            indexes = vector_collection.index_information()
            logger.info(f"Collection indexes: {list(indexes.keys())}")
            logger.info(f"Checking for vector search index in MongoDB Atlas")
        except Exception as e:
            logger.error(f"Error checking indexes: {str(e)}")
        
        # Get a sample document to examine its structure
        sample = vector_collection.find_one({})
        if sample:
            logger.info(f"Sample document fields: {list(sample.keys())}")
            if 'embedding' in sample:
                logger.info(f"Embedding field exists with length: {len(sample['embedding'])}")
            else:
                logger.error("No 'embedding' field found in document!")
        
        # Try a simple test query
        test_query = "What are the basics of Vedic astrology?"
        logger.info(f"Testing RAG model with query: '{test_query}'")
        
        # First try direct retrieval without vector search to verify docs exist
        basic_docs = list(vector_collection.find().limit(2))
        logger.info(f"Direct retrieval test: Found {len(basic_docs)} documents")
        
        # Now try vector search
        relevant_docs = search_similar_pdfs(test_query, top_k=2)
        
        if relevant_docs and len(relevant_docs) > 0:
            logger.info(f"Successfully retrieved {len(relevant_docs)} relevant documents")
            
            # Print a sample of each document
            for i, doc in enumerate(relevant_docs):
                if 'text' in doc:
                    sample = doc['text'][:150] + "..." if len(doc['text']) > 150 else doc['text']
                    logger.info(f"Document {i+1} sample: {sample}")
                    
            return True
        else:
            logger.warning("No relevant documents found for the test query")
            # Try fallback search method
            logger.info("Trying fallback search method...")
            try:
                # Simple text search without vector index
                fallback_docs = list(vector_collection.find({"$text": {"$search": test_query}}).limit(2))
                if fallback_docs:
                    logger.info(f"Fallback search found {len(fallback_docs)} documents")
                else:
                    logger.warning("Fallback search also found no documents")
            except Exception as e:
                logger.error(f"Fallback search error: {str(e)}")
            
            return False
            
    except Exception as e:
        logger.error(f"Error testing RAG model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("RAG Model Initialization")
    print("=" * 80)
    
    # Check if specific files are provided as command line arguments
    specific_files = None
    if len(sys.argv) > 1:
        specific_files = sys.argv[1:]
        print(f"Using specific files: {', '.join(specific_files)}")
    
    init_success = initialize_rag(specific_files)
    
    if init_success:
        print("\n✅ RAG model initialized successfully")
        
        # Test the RAG model
        print("\nTesting RAG model query capability...")
        test_success = test_rag_query()
        
        if test_success:
            print("\n✅ RAG model query test successful")
        else:
            print("\n❌ RAG model query test failed")
    else:
        print("\n❌ RAG model initialization failed")
    
    print("\nDone!")