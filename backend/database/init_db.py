# database/init_db.py
from pymongo import MongoClient, ASCENDING # type: ignore
from pymongo.errors import CollectionInvalid # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import logging

logger = logging.getLogger(__name__)

def init_mongodb():
    """Initialize MongoDB with required collections and indexes"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Connect to MongoDB
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('MONGODB_DATABASE')]
        
        # Initialize Users Collection
        try:
            db.create_collection('users')
        except CollectionInvalid:
            logger.info("Users collection already exists")
        
        users = db['users']
        
        # Create indexes
        users.create_index([('email', ASCENDING)], unique=True)
        users.create_index([('verification_token', ASCENDING)])
        
        # Initialize Horoscopes Collection
        try:
            db.create_collection('horoscopes')
        except CollectionInvalid:
            logger.info("Horoscopes collection already exists")
        
        horoscopes = db['horoscopes']
        
        # Create indexes for horoscopes
        horoscopes.create_index([('user_id', ASCENDING)])
        horoscopes.create_index([('created_at', ASCENDING)])
        
        # Initialize Conversations Collection
        try:
            db.create_collection('conversations')
        except CollectionInvalid:
            logger.info("Conversations collection already exists")
        
        conversations = db['conversations']
        
        # Create indexes for conversations
        conversations.create_index([('user_id', ASCENDING)])
        conversations.create_index([('created_at', ASCENDING)])
        
        logger.info("MongoDB initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    if init_mongodb():
        print("Database initialized successfully")
    else:
        print("Error initializing database")