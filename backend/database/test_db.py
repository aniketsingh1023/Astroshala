# database/test_db.py
from pymongo import MongoClient # type: ignore
from werkzeug.security import generate_password_hash # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Connect to MongoDB
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('MONGODB_DATABASE')]
        
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Test user creation
        users = db['users']
        
        test_user = {
            'email': 'test@example.com',
            'password': generate_password_hash('Test123!'),
            'name': 'Test User',
            'is_verified': False,
            'verification_token': 'test_token',
            'verification_expiry': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Check if test user exists
        existing_user = users.find_one({'email': test_user['email']})
        
        if existing_user:
            logger.info(f"Test user already exists: {test_user['email']}")
            # Update user
            result = users.update_one(
                {'email': test_user['email']},
                {'$set': {'updated_at': datetime.utcnow()}}
            )
            logger.info(f"Updated test user: {result.modified_count}")
        else:
            # Insert test user
            result = users.insert_one(test_user)
            logger.info(f"Created test user with ID: {result.inserted_id}")
        
        # Test user retrieval
        found_user = users.find_one({'email': test_user['email']})
        if found_user:
            logger.info("Successfully retrieved test user")
        
        # Test other collections
        horoscopes = db['horoscopes']
        conversations = db['conversations']
        
        logger.info(f"Available collections: {db.list_collection_names()}")
        
        return True
        
    except Exception as e:
        logger.error(f"MongoDB test failed: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()
            logger.info("MongoDB connection closed")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    if test_mongodb_connection():
        print("MongoDB connection test passed")
    else:
        print("MongoDB connection test failed")