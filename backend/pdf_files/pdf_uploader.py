# pdf_uploader.py
"""
Utility to upload PDF files to MongoDB GridFS and process them for the RAG model.
This approach bypasses file system issues by storing PDFs directly in the database.
"""
import os
import sys
import logging
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId
from PyPDF2 import PdfReader
from io import BytesIO
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Text splitter for chunking documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, chunk_overlap=16
)

# Initialize embedding model
embedding_model = HuggingFaceEmbeddings(model_name='thenlper/gte-large')

def generate_embedding(text):
    """Generate embedding vector for text"""
    return embedding_model.embed_query(text)

def connect_to_mongodb():
    """Connect to MongoDB and return client, db, GridFS, and collections"""
    try:
        # Get MongoDB connection details
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
            
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        client.admin.command('ping')  # Test connection
        logger.info("MongoDB connection successful")
        
        # Get database
        db_name = os.getenv("MONGODB_DATABASE", "vector_db")
        db = client[db_name]
        
        # Initialize GridFS for file storage
        fs = GridFS(db, collection="pdfs")
        
        # Get collections
        pdf_collection = db["pdfs.files"]
        vector_collection = db[os.getenv("COLLECTION_NAME", "pdf_documents")]
        
        return client, db, fs, pdf_collection, vector_collection
    
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        raise

def upload_pdf(file_path):
    """Upload a PDF file to MongoDB GridFS"""
    try:
        # Validate file
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        if not file_path.lower().endswith('.pdf'):
            logger.error(f"Not a PDF file: {file_path}")
            return None
        
        # Connect to MongoDB
        client, db, fs, pdf_collection, _ = connect_to_mongodb()
        
        # Check if file already exists (by name)
        filename = os.path.basename(file_path)
        existing_file = pdf_collection.find_one({"filename": filename})
        if existing_file:
            logger.info(f"File '{filename}' already exists with ID: {existing_file['_id']}")
            return str(existing_file['_id'])
            
        # Read file and upload to GridFS
        with open(file_path, 'rb') as f:
            file_data = f.read()
            file_id = fs.put(
                file_data, 
                filename=filename,
                content_type="application/pdf"
            )
            
        logger.info(f"Uploaded file '{filename}' with ID: {file_id}")
        return str(file_id)
        
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None
        
def process_pdf_from_gridfs(file_id):
    """Process a PDF from GridFS and extract text chunks"""
    try:
        # Connect to MongoDB
        client, db, fs, _, _ = connect_to_mongodb()
        
        # Get file from GridFS
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
            
        if not fs.exists(file_id):
            logger.error(f"File with ID {file_id} not found in GridFS")
            return []
            
        # Get file data
        grid_file = fs.get(file_id)
        pdf_data = grid_file.read()
        
        # Extract text from PDF
        pdf_file = BytesIO(pdf_data)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
                
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        logger.info(f"Extracted {len(chunks)} text chunks from PDF with ID: {file_id}")
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing PDF from GridFS: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def process_and_embed_all_pdfs():
    """Process all PDFs in GridFS and create vector embeddings"""
    try:
        # Connect to MongoDB
        client, db, fs, pdf_collection, vector_collection = connect_to_mongodb()
        
        # Get all PDF files in GridFS
        pdf_files = list(pdf_collection.find())
        if not pdf_files:
            logger.error("No PDF files found in GridFS")
            return 0
            
        logger.info(f"Found {len(pdf_files)} PDF files in GridFS")
        
        # Process each PDF and create vector embeddings
        total_chunks = 0
        for pdf_file in pdf_files:
            file_id = pdf_file['_id']
            filename = pdf_file['filename']
            
            logger.info(f"Processing PDF: {filename}")
            
            # Extract text chunks from PDF
            chunks = process_pdf_from_gridfs(file_id)
            if not chunks:
                logger.warning(f"No text chunks extracted from {filename}")
                continue
                
            # Create vector embeddings for chunks
            documents = []
            for i, chunk in enumerate(chunks):
                embedding = generate_embedding(chunk)
                documents.append({
                    "text": chunk,
                    "embedding": embedding,
                    "pdf_id": str(file_id),
                    "filename": filename,
                    "chunk_index": i
                })
                
            # Insert into vector collection
            if documents:
                vector_collection.insert_many(documents)
                total_chunks += len(documents)
                
        logger.info(f"Created vector embeddings for {total_chunks} text chunks")
        return total_chunks
        
    except Exception as e:
        logger.error(f"Error processing PDFs: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0

def list_uploaded_pdfs():
    """List all PDFs uploaded to GridFS"""
    try:
        # Connect to MongoDB
        client, db, fs, pdf_collection, _ = connect_to_mongodb()
        
        # Get all PDF files
        pdf_files = list(pdf_collection.find())
        
        if not pdf_files:
            print("No PDF files found in MongoDB")
            return
            
        print("\nPDFs in MongoDB GridFS:")
        print("-" * 80)
        print(f"{'ID':<24} | {'Filename':<30} | {'Size':<10} | {'Upload Date'}")
        print("-" * 80)
        
        for pdf in pdf_files:
            file_id = str(pdf['_id'])
            filename = pdf['filename']
            size = pdf['length'] / 1024  # Size in KB
            upload_date = pdf['uploadDate']
            
            print(f"{file_id:<24} | {filename:<30} | {size:<10.2f} KB | {upload_date}")
            
    except Exception as e:
        logger.error(f"Error listing PDFs: {str(e)}")

def search_similar_text(query, top_k=3):
    """Search for similar text chunks based on a query"""
    try:
        # Connect to MongoDB
        client, db, _, _, vector_collection = connect_to_mongodb()
        
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Perform vector search
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
            },
            {
                "$project": {
                    "text": 1,
                    "pdf_id": 1,
                    "filename": 1,
                    "chunk_index": 1,
                    "score": { "$meta": "searchScore" }
                }
            }
        ])
        
        return list(results)
        
    except Exception as e:
        logger.error(f"Error searching similar text: {str(e)}")
        return []

def clear_vector_store():
    """Clear all vector embeddings but keep PDF files"""
    try:
        # Connect to MongoDB
        client, db, _, _, vector_collection = connect_to_mongodb()
        
        # Count documents before deletion
        count_before = vector_collection.count_documents({})
        
        # Delete all documents
        result = vector_collection.delete_many({})
        
        logger.info(f"Deleted {result.deleted_count}/{count_before} vector embeddings")
        return result.deleted_count
        
    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}")
        return 0

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PDF Manager for RAG System")
    print("=" * 80)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python pdf_uploader.py upload <pdf_file1> [pdf_file2 ...]")
        print("  python pdf_uploader.py process")
        print("  python pdf_uploader.py list")
        print("  python pdf_uploader.py search \"<query>\"")
        print("  python pdf_uploader.py clear")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    
    if command == "upload":
        if len(sys.argv) < 3:
            print("Error: Please specify at least one PDF file to upload")
            sys.exit(1)
            
        files = sys.argv[2:]
        for file_path in files:
            file_id = upload_pdf(file_path)
            if file_id:
                print(f"✅ Uploaded {os.path.basename(file_path)} (ID: {file_id})")
            else:
                print(f"❌ Failed to upload {file_path}")
                
    elif command == "process":
        print("\nProcessing PDFs and creating vector embeddings...")
        chunk_count = process_and_embed_all_pdfs()
        if chunk_count > 0:
            print(f"✅ Successfully processed {chunk_count} text chunks")
        else:
            print("❌ Failed to process PDFs")
            
    elif command == "list":
        list_uploaded_pdfs()
        
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please specify a query")
            sys.exit(1)
            
        query = sys.argv[2]
        print(f"\nSearching for: '{query}'")
        
        results = search_similar_text(query, top_k=3)
        if not results:
            print("No results found")
        else:
            print(f"\nFound {len(results)} matches:")
            print("-" * 80)
            
            for i, result in enumerate(results):
                print(f"Match {i+1}:")
                print(f"File: {result.get('filename', 'Unknown')}")
                print(f"Text: {result.get('text', '')[:150]}...")
                print(f"Score: {result.get('score', 0):.4f}")
                print("-" * 80)
                
    elif command == "clear":
        confirm = input("Are you sure you want to clear all vector embeddings? (yes/no): ")
        if confirm.lower() == "yes":
            deleted = clear_vector_store()
            print(f"✅ Cleared {deleted} vector embeddings")
        else:
            print("Operation cancelled")
            
    else:
        print(f"Unknown command: {command}")
        print("Available commands: upload, process, list, search, clear")