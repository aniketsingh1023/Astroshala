# models/user.py
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class User:
    """User model for MongoDB interaction"""
    
    def __init__(self, email=None, password=None, name=None, 
                 verification_token=None, verification_expiry=None,
                 is_verified=False, birth_details=None):
        """Initialize a new user instance"""
        self.email = email
        self.password = password
        self.name = name
        self.verification_token = verification_token
        self.verification_expiry = verification_expiry
        self.is_verified = is_verified
        self.birth_details = birth_details or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Initialize MongoDB connection
        self.client = None
        self.db = None
        self.collection = None
        self._connect_to_mongodb()

    def _connect_to_mongodb(self):
        """Connect to MongoDB database"""
        try:
            self.client = MongoClient(os.getenv('MONGODB_URI'))
            self.db = self.client[os.getenv('MONGODB_DATABASE')]
            self.collection = self.db['users']
        except Exception as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            raise

    @classmethod
    def _get_collection(cls):
        """Get MongoDB collection (static method)"""
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('MONGODB_DATABASE')]
        return db['users'], client

    def save(self) -> Optional[str]:
        """
        Save the user instance to MongoDB
        Returns user_id if successful, None if failed
        """
        try:
            user_doc = {
                'email': self.email.lower(),
                'password': self.password,
                'name': self.name,
                'verification_token': self.verification_token,
                'verification_expiry': self.verification_expiry,
                'is_verified': self.is_verified,
                'birth_details': self.birth_details,
                'created_at': self.created_at,
                'updated_at': self.updated_at
            }
            
            result = self.collection.insert_one(user_doc)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving user: {str(e)}")
            return None

    @classmethod
    def find_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by email (class method)
        """
        collection, client = cls._get_collection()
        try:
            user = collection.find_one({'email': email.lower()})
            return user
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            return None
        finally:
            if client:
                client.close()

    @classmethod
    def find_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by ID (class method)
        """
        collection, client = cls._get_collection()
        try:
            user = collection.find_one({'_id': ObjectId(user_id)})
            return user
        except Exception as e:
            logger.error(f"Error finding user by ID: {str(e)}")
            return None
        finally:
            if client:
                client.close()

    @classmethod
    def find_by_verification_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by verification token (class method)
        """
        collection, client = cls._get_collection()
        try:
            user = collection.find_one({'verification_token': token})
            return user
        except Exception as e:
            logger.error(f"Error finding user by token: {str(e)}")
            return None
        finally:
            if client:
                client.close()

    @classmethod
    def verify_email(cls, user_id: str) -> bool:
        """
        Mark user's email as verified (class method)
        """
        collection, client = cls._get_collection()
        try:
            result = collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'is_verified': True,
                        'verification_token': None,
                        'verification_expiry': None,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error verifying email: {str(e)}")
            return False
        finally:
            if client:
                client.close()

    @classmethod
    def update_verification_token(cls, user_id: str, token: str, expiry: datetime) -> bool:
        """
        Update user's verification token (class method)
        """
        collection, client = cls._get_collection()
        try:
            result = collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'verification_token': token,
                        'verification_expiry': expiry,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating verification token: {str(e)}")
            return False
        finally:
            if client:
                client.close()

    @classmethod
    def update_birth_details(cls, user_id: str, birth_details: Dict[str, Any]) -> bool:
        """
        Update user's birth details (class method)
        """
        collection, client = cls._get_collection()
        try:
            result = collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'birth_details': birth_details,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating birth details: {str(e)}")
            return False
        finally:
            if client:
                client.close()

    @classmethod
    def update_profile(cls, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Update user's profile information (class method)
        """
        collection, client = cls._get_collection()
        try:
            update_fields = {
                'updated_at': datetime.utcnow()
            }
            
            if 'name' in profile_data:
                update_fields['name'] = profile_data['name']
            
            if 'birth_details' in profile_data:
                update_fields['birth_details'] = profile_data['birth_details']

            result = collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_fields}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return False
        finally:
            if client:
                client.close()

    @classmethod
    def get_all_users(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all users (class method)
        """
        collection, client = cls._get_collection()
        try:
            users = list(collection.find({}, {'password': 0}).limit(limit))
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
        finally:
            if client:
                client.close()

    @classmethod
    def delete_user(cls, user_id: str) -> bool:
        """
        Delete a user account (class method)
        """
        collection, client = cls._get_collection()
        try:
            result = collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
        finally:
            if client:
                client.close()