# routes/chat_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from pymongo import MongoClient
import os
from datetime import datetime
import logging
import traceback
from openai import OpenAI
from bson import ObjectId
from vector_store import search_similar_pdfs

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/query', methods=['OPTIONS'])
@chat_bp.route('/start', methods=['OPTIONS'])
@chat_bp.route('/history', methods=['OPTIONS'])
@chat_bp.route('/conversations', methods=['OPTIONS'])
def handle_options():
    """Handle OPTIONS requests for chat endpoints"""
    logger.info(f"Handling OPTIONS request in chat_bp for {request.path}")
    return '', 200

# Initialize MongoDB client
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DATABASE", "vector_db")]
conversations_collection = db["conversations"]
messages_collection = db["messages"]

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt for astrology context
ASTROLOGY_SYSTEM_PROMPT = """
You are an expert Parasara Jyotish astrologer with deep knowledge of Vedic astrology.
Provide detailed and insightful responses based on traditional Vedic astrological principles.
Be concise but thorough in your explanations.

When appropriate, ask for the user's birth details (date, time, and place of birth) 
if they haven't provided them and their question would benefit from personalized analysis.
"""

def generate_response_with_rag(user_message, conversation_history=None, birth_details=None):
    """Generate a response using RAG approach"""
    try:
        # Get relevant documents
        relevant_documents = search_similar_pdfs(user_message, top_k=5)
        context = ""
        
        if relevant_documents and len(relevant_documents) > 0:
            logger.info(f"Found {len(relevant_documents)} relevant documents")
            context_list = []
            for doc in relevant_documents:
                if 'text' in doc:
                    context_list.append(doc['text'])
            context = " ".join(context_list)
        else:
            logger.warning("No relevant documents found for the query")
            context = "No specific information found in the knowledge base for this query."
        
        # Build messages array for OpenAI
        messages = [{"role": "system", "content": ASTROLOGY_SYSTEM_PROMPT}]
        
        # Add birth details if available
        if birth_details:
            birth_context = f"""
            The user has provided these birth details:
            Date: {birth_details.get('date', 'Not provided')}
            Time: {birth_details.get('time', 'Not provided')}
            Place: {birth_details.get('place', 'Not provided')}
            
            Use these details in your analysis when relevant.
            """
            messages.append({"role": "system", "content": birth_context})
        
        # Add context from RAG
        messages.append({"role": "system", "content": f"Use the following context from Vedic astrology texts to inform your answer: {context}"})
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add the user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response from OpenAI
        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error generating RAG response: {str(e)}")
        return f"I encountered an error generating a response. Please try again later."

def handle_auth_optional_request():
    """Handle both authenticated and unauthenticated requests"""
    # Check if request has JWT
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        current_user_id = None
    
    return current_user_id

@chat_bp.route('/query', methods=['POST', 'OPTIONS'])
def chat_query():
    """Universal chat endpoint that works for both authenticated and unauthenticated users"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get request data
        data = request.json or {}
        
        # Validate input
        if not data.get('message') and not data.get('query'):
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Get message from either field
        user_message = data.get('message') or data.get('query')
        conversation_id = data.get('conversation_id')
        birth_details = data.get('birth_details', {})
        conversation_history = data.get('conversation_history', [])
        
        logger.info(f"Chat query received: {user_message[:30]}...")
        
        # Check for authentication
        current_user_id = handle_auth_optional_request()
        
        # If authenticated and conversation ID provided, use existing conversation
        if current_user_id and conversation_id:
            try:
                # Verify conversation exists and belongs to the user
                conversation = conversations_collection.find_one({
                    "_id": ObjectId(conversation_id),
                    "user_id": ObjectId(current_user_id)
                })
                
                if conversation:
                    # Get conversation history
                    messages_cursor = messages_collection.find({
                        "conversation_id": conversation_id
                    }).sort("timestamp", 1)
                    
                    history = list(messages_cursor)
                    
                    # Get birth details from conversation if not provided
                    if not birth_details:
                        birth_details = conversation.get('birth_details', {})
                    
                    # Generate response
                    response_text = generate_response_with_rag(user_message, history, birth_details)
                    
                    # Store messages in MongoDB
                    current_time = datetime.utcnow()
                    
                    # Store user message
                    messages_collection.insert_one({
                        "conversation_id": conversation_id,
                        "role": "user",
                        "content": user_message,
                        "timestamp": current_time
                    })
                    
                    # Store assistant response
                    messages_collection.insert_one({
                        "conversation_id": conversation_id,
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": current_time
                    })
                    
                    # Update conversation last_updated timestamp
                    conversations_collection.update_one(
                        {"_id": ObjectId(conversation_id)},
                        {"$set": {"last_updated": current_time}}
                    )
                    
                    return jsonify({
                        'success': True,
                        'response': response_text,
                        'conversation_id': conversation_id
                    }), 200
            except Exception as e:
                logger.error(f"Error in authenticated conversation flow: {str(e)}")
                # Continue to fallback flow
        
        # For new authenticated conversations or unauthenticated users
        if current_user_id and not conversation_id:
            # Create new conversation
            current_time = datetime.utcnow()
            conversation_result = conversations_collection.insert_one({
                "user_id": ObjectId(current_user_id),
                "created_at": current_time,
                "last_updated": current_time,
                "birth_details": birth_details
            })
            
            conversation_id = str(conversation_result.inserted_id)
            logger.info(f"Created new conversation: {conversation_id}")
            
            # Generate response
            response_text = generate_response_with_rag(user_message, None, birth_details)
            
            # Store messages in MongoDB
            # Store user message
            messages_collection.insert_one({
                "conversation_id": conversation_id,
                "role": "user",
                "content": user_message,
                "timestamp": current_time
            })
            
            # Store assistant response
            messages_collection.insert_one({
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": response_text,
                "timestamp": current_time
            })
            
            return jsonify({
                'success': True,
                'response': response_text,
                'conversation_id': conversation_id
            }), 200
        
        # For unauthenticated users or fallback
        # Use conversation history if provided
        response_text = generate_response_with_rag(user_message, conversation_history, birth_details)
        
        return jsonify({
            'success': True,
            'response': response_text
        }), 200
        
    except Exception as e:
        logger.error(f"Chat query error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to process query',
            'details': str(e)
        }), 500

@chat_bp.route('/start', methods=['POST'])
@jwt_required()
def start_conversation():
    """Start a new conversation (authenticated)"""
    try:
        logger.info("Chat conversation start requested")
        
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Get request data
        data = request.json or {}
        
        # Extract birth details
        birth_details = data.get('birth_details', {})
        
        # Create new conversation in MongoDB
        current_time = datetime.utcnow()
        conversation_result = conversations_collection.insert_one({
            "user_id": ObjectId(current_user_id),
            "created_at": current_time,
            "last_updated": current_time,
            "birth_details": birth_details
        })
        
        conversation_id = str(conversation_result.inserted_id)
        
        # Generate welcome message
        welcome_message = "Welcome to Parasara Jyotish consultation! I'm your astrological assistant. How can I help you today?"
        
        # Store assistant welcome message
        messages_collection.insert_one({
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": welcome_message,
            "timestamp": current_time
        })
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'initial_response': welcome_message
        }), 200
    
    except Exception as e:
        logger.error(f"Conversation start error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to start conversation',
            'details': str(e)
        }), 500

@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    """Retrieve chat conversation history (authenticated)"""
    try:
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Get conversation ID from query params
        conversation_id = request.args.get('conversation_id')
        if not conversation_id:
            return jsonify({
                'success': False,
                'error': 'Conversation ID is required'
            }), 400
            
        # Verify conversation exists and belongs to the user
        conversation = conversations_collection.find_one({
            "_id": ObjectId(conversation_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        # Get messages for this conversation
        messages_cursor = messages_collection.find({
            "conversation_id": conversation_id
        }).sort("timestamp", 1)
        
        # Format messages for the response
        messages = []
        for msg in messages_cursor:
            messages.append({
                'id': str(msg['_id']),
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': msg['timestamp'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'messages': messages,
            'total_messages': len(messages)
        }), 200
    
    except Exception as e:
        logger.error(f"Chat history retrieval error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve chat history',
            'details': str(e)
        }), 500

@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get list of user's conversations (authenticated)"""
    try:
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Get all conversations for this user
        conversations_cursor = conversations_collection.find({
            "user_id": ObjectId(current_user_id)
        }).sort("last_updated", -1)
        
        # Format conversations for the response
        conversations = []
        for conv in conversations_cursor:
            # Get first message to use as title
            first_message = messages_collection.find_one({
                "conversation_id": str(conv['_id']),
                "role": "user"
            })
            
            title = "New Conversation"
            if first_message:
                # Use first 30 chars of first message as title
                title = first_message['content'][:30] + ('...' if len(first_message['content']) > 30 else '')
            
            conversations.append({
                'id': str(conv['_id']),
                'title': title,
                'created_at': conv['created_at'].isoformat(),
                'last_updated': conv['last_updated'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'conversations': conversations,
            'total_conversations': len(conversations)
        }), 200
    
    except Exception as e:
        logger.error(f"Conversations retrieval error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversations',
            'details': str(e)
        }), 500