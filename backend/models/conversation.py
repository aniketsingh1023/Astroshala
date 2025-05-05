# models/conversation.py
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime
from dotenv import load_dotenv # type: ignore

load_dotenv()

class Conversation:
    def __init__(self, user_id, initial_context=None):
        self.user_id = user_id
        self.initial_context = initial_context or {}
        self.messages = []
        self.started_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()

    @staticmethod
    def get_collection():
        """
        Get the MongoDB collection for conversations
        """
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('MONGODB_DATABASE')]
        return db['conversations']

    def add_message(self, message, sender):
        """
        Add a message to the conversation
        """
        self.messages.append({
            'message': message,
            'sender': sender,
            'timestamp': datetime.utcnow()
        })
        self.last_updated = datetime.utcnow()

    def save(self):
        """
        Save conversation to the database
        """
        collection = self.get_collection()
        conversation_data = {
            'user_id': ObjectId(self.user_id),
            'initial_context': self.initial_context,
            'messages': self.messages,
            'started_at': self.started_at,
            'last_updated': self.last_updated
        }
        return collection.insert_one(conversation_data)

    @classmethod
    def find_by_user_id(cls, user_id, limit=50):
        """
        Find conversations for a specific user
        """
        collection = cls.get_collection()
        return list(collection.find(
            {'user_id': ObjectId(user_id)}
        ).sort('last_updated', -1).limit(limit))

    @classmethod
    def get_recent_conversation(cls, user_id):
        """
        Get the most recent conversation for a user
        """
        collection = cls.get_collection()
        return collection.find_one(
            {'user_id': ObjectId(user_id)},
            sort=[('last_updated', -1)]
        )