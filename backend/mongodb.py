# test_mongodb_connection.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import sys

def test_mongodb_connection():
    """Test connection to MongoDB and authenticate user."""
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string from .env or use hardcoded value for testing
    mongodb_uri = os.getenv("MONGODB_URI")
    
    if not mongodb_uri:
        print("WARNING: No MONGODB_URI found in environment variables. Using hardcoded value for testing.")
        mongodb_uri = "mongodb+srv://sohamnsharma:rdcv4c75@astroveddb.ari36.mongodb.net/?retryWrites=true&w=majority&appName=astrovedDB"
    
    print(f"Testing connection to: {mongodb_uri}")
    
    try:
        # Try to connect
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Force server selection to verify connection
        client.admin.command('ping')
        
        print("Connection successful! Connected to MongoDB.")
        
        # Print available databases to verify permissions
        db_names = client.list_database_names()
        print(f"Available databases: {db_names}")
        
        # Get database name from .env or use default
        db_name = os.getenv("MONGODB_DATABASE", "vector_db")
        collection_name = os.getenv("COLLECTION_NAME", "pdf_documents")
        
        # Check if the database exists
        if db_name in db_names:
            db = client[db_name]
            print(f"Database '{db_name}' exists.")
            
            # Check collections
            collection_names = db.list_collection_names()
            print(f"Collections in {db_name}: {collection_names}")
            
            # Check if our target collection exists
            if collection_name in collection_names:
                print(f"Collection '{collection_name}' exists.")
                # Count documents
                count = db[collection_name].count_documents({})
                print(f"Document count in {collection_name}: {count}")
            else:
                print(f"Collection '{collection_name}' does not exist yet.")
        else:
            print(f"Database '{db_name}' does not exist yet.")
        
        # Try to check if vector search is configured
        try:
            index_info = client[db_name][collection_name].index_information()
            print(f"Index information: {index_info}")
        except Exception as e:
            print(f"Could not retrieve index information: {e}")
        
        return True
    
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()
            print("MongoDB connection closed.")

if __name__ == "__main__":
    print("\n=== MongoDB Connection Test ===\n")
    success = test_mongodb_connection()
    
    print("\n=== Test Result ===")
    if success:
        print("SUCCESS: MongoDB connection is working properly.")
        sys.exit(0)
    else:
        print("FAILED: Could not connect to MongoDB. Check your credentials and network.")
        sys.exit(1)