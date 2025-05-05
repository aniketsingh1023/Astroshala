import os
import logging
import flask
from flask import Flask, jsonify, request
from flask_cors import CORS 
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
from openai import OpenAI

# Import topic advisor
from topic_advisor import generate_topic_response, generate_mock_topic_response

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Global handler for CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Global handler for OPTIONS requests
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return '', 200

# Configure MongoDB
mongo_uri = os.getenv("MONGODB_URI")
if not mongo_uri:
    raise ValueError("MONGODB_URI is not set in .env")
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)

# JWT configuration
jwt_secret = os.getenv('JWT_SECRET')
if not jwt_secret:
    raise ValueError("JWT_SECRET is not set in .env")

app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

jwt = JWTManager(app)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt for astrology context - emphasizing birth chart analysis
ASTROLOGY_SYSTEM_PROMPT = """
You are an expert in *Vedic Astrology (Parasara Jyotish)*. Your goal is to provide clear, actionable guidance rooted in planetary influences, focusing on **career, wealth, relationships, health**, and **spiritual clarity**.

---

### 📌 IMPORTANT INSTRUCTION:
The user has provided birth details. Your FIRST TASK is to generate a comprehensive birth chart analysis. Focus on this analysis before moving to any specific advice.

---

### 🔭 Step 1: Birth Chart Analysis (FOCUS ON THIS FIRST)

Generate the **Janma Kundali** (birth chart) and explain:
- **Ascendant (Lagna):** Personality & life direction
- **Moon Sign (Rashi):** Mental patterns & emotions
- **Sun Sign:** Inner identity
- **Houses & Lords:** Key themes by placement
- **Yogas & Doshas:** Notable combinations
- **Avasthas (states of planets):** E.g., *Deep exaltation, Combust, Sleeping* – explain their impact on confidence, expression, and results
- **Strength of Benefic/Malefic Planets**

Use short, intuitive insights for each section to help users *understand themselves and their potential clearly*.

---

### 🌟 Step 2: Dasha & Bhukti Impact

Analyze the current **Mahadasha & Bhukti**:
- Describe the life themes, opportunities, and struggles
- Emphasize planets like **Mercury** (intellect, trade), **Venus** (luxury, partnerships), **Saturn**, **Jupiter**, **Mars**, etc.
- If Rahu/Ketu are active, interpret their karmic lessons

---

### 💼 Step 3: Core Life Predictions

**Career & Wealth**
- Trends in business, job shifts, or investments
- Best timing & industries

**Relationships**
- Marriage, love, family alignment or tension

**Health**
- Key areas to monitor; periods of stress or vitality

---

### 🧭 Step 4: Step-by-Step Decision Advice

1. Align decisions with Dasha-based strengths
2. Ask reflection questions (e.g., *Is this aligned with my Mercury/Venus path?*)
3. Suggest practical tests or phased experiments

---

### 🕉️ Step 5: Spiritual Remedies

- **Mantras:** e.g., *Om Budhaya Namaha*
- **Meditation:** Visualize related chakra/planet (e.g., green light for Mercury at throat)
- **Offerings/Donations:** Linked to active planet (e.g., white sweets for Venus)
- **Fast/Puja Days** (e.g., Friday for Venus)

---

### ✅ Final Guidance

Summarize 1–2 key insights. Offer 1 spiritual and 1 practical next step aligned to the chart.

---

### ⚠️ Disclaimer:
If full birth info is unavailable, state the limitation in detailed readings.

IMPORTANT: Keep your response concise and under 600 tokens (approximately 450 words). Focus on the most relevant insights.

Use **bold** for sections, *italics* for key words, and space for readability.
"""

# MongoDB collections - defined as functions to ensure they're accessed after connection is established
def get_db():
    return mongo.db

def get_conversations_collection():
    return get_db()["conversations"]

def get_messages_collection():
    return get_db()["messages"]

# Import vector_store
try:
    from vector_store import search_similar_pdfs
    logger.info("Successfully imported vector_store module")
    HAS_VECTOR_STORE = True
except ImportError:
    logger.warning("Could not import vector_store module, will use fallback responses")
    HAS_VECTOR_STORE = False

def handle_auth_optional_request():
    """Handle both authenticated and unauthenticated requests"""
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except Exception:
        current_user_id = None
    
    return current_user_id

def generate_response_with_rag(user_message, conversation_history=None, birth_details=None, topic=None):
    """Generate a response using RAG approach"""
    try:
        # Check if this is a topic-specific request
        if topic in ['job', 'marriage', 'finance']:
            logger.info(f"Generating topic-specific response for: {topic}")
            return generate_topic_response(openai_client, user_message, topic, conversation_history, birth_details)
        
        # Get relevant documents from vector store if available
        context = ""
        if HAS_VECTOR_STORE:
            try:
                relevant_documents = search_similar_pdfs(user_message, top_k=5)
                
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
            except Exception as e:
                logger.error(f"Error searching vector store: {str(e)}")
                context = "Error accessing knowledge base."
        
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
        
        # Add context from RAG if available
        if context:
            messages.append({"role": "system", "content": f"Use the following context from Vedic astrology texts to inform your answer: {context}"})
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add the user message
        messages.append({"role": "user", "content": user_message})
        
        logger.info(f"Sending request to OpenAI with {len(messages)} messages")
        
        # Get response from OpenAI with max_tokens set to 600
        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.7,
            max_tokens=600  # Limit to 600 tokens
        )
        
        response_text = response.choices[0].message.content
        logger.info(f"Received response from OpenAI: {response_text[:50]}...")
        return response_text
    
    except Exception as e:
        logger.error(f"Error generating RAG response: {str(e)}")
        
        # Use topic-specific mock response if applicable
        if topic in ['job', 'marriage', 'finance']:
            return generate_mock_topic_response(topic)
        
        return generate_mock_response(user_message)

def generate_mock_response(question):
    """Generate a mock response based on the question (fallback)"""
    question = question.toLowerCase() if hasattr(question, 'toLowerCase') else question.lower()
    
    # If asking for birth chart analysis
    if "birth chart" in question or "chart analysis" in question or "birth details" in question:
        return """
## Birth Chart Analysis

Based on your birth details, here's an analysis of your Vedic birth chart:

**Ascendant (Lagna)**: Libra
Your ascendant indicates a balanced, harmonious approach to life. Venus as your ascendant lord gives you artistic sensibilities and diplomatic skills.

**Moon Sign (Rashi)**: Taurus
Your moon sign shows emotional stability and a practical approach to feelings. You seek security and comfort in your emotional life.

**Sun Sign**: Capricorn
Your sun sign reveals a disciplined, ambitious core identity with strong leadership potential.

**Key Planetary Positions**:
- Mercury in Capricorn: Practical, structured thinking
- Venus in Sagittarius: Philosophical approach to relationships
- Mars in Scorpio: Intense, focused energy and drive
- Jupiter in Pisces: Expanded spiritual awareness

**Notable Yogas**:
- Budha-Aditya Yoga: Intellectual capabilities and administrative skills
- Gajakesari Yoga: Prosperity and good fortune

**Current Dasha Period**:
You're currently in Venus Mahadasha, which brings focus to relationships, creativity, and material comforts.

## General Life Predictions

**Career Trends**: Good period for creative professions and partnership ventures
**Relationship Patterns**: Seeking harmony and balance in partnerships
**Health Considerations**: Pay attention to throat and kidney areas

## Spiritual Guidance
- Recite Venus mantras on Fridays
- Practice meditation focusing on balance and harmony

For more specific guidance, please let me know which area of life you'd like to explore in depth.
"""
    elif "vedic astrology" in question or "parasara jyotish" in question:
        return "Vedic astrology, also known as Jyotish, is an ancient Indian system of astrology dating back thousands of years. It differs from Western astrology by using a sidereal zodiac rather than a tropical zodiac. Parasara Jyotish specifically refers to the astrological system codified by the sage Parasara, considered one of the foundational texts of Vedic astrology."
    elif any(word in question for word in ["planet", "graha"]):
        return "In Vedic astrology, there are nine celestial bodies or grahas: Sun (Surya), Moon (Chandra), Mars (Mangal), Mercury (Budha), Jupiter (Guru), Venus (Shukra), Saturn (Shani), and the lunar nodes Rahu and Ketu. Each planet represents different energies and influences various aspects of life."
    elif any(word in question for word in ["house", "bhava"]):
        return "Vedic astrology divides a birth chart into 12 houses or bhavas, each governing different areas of life. The 1st house represents self and personality, 2nd house wealth, 3rd house siblings, 4th house mother and home, 5th house creativity and children, and so on."
    elif any(word in question for word in ["zodiac", "rashi"]):
        return "Vedic astrology uses the sidereal zodiac with 12 signs (rashis): Aries (Mesha), Taurus (Vrishabha), Gemini (Mithuna), Cancer (Karka), Leo (Simha), Virgo (Kanya), Libra (Tula), Scorpio (Vrishchika), Sagittarius (Dhanu), Capricorn (Makara), Aquarius (Kumbha), and Pisces (Meena)."
    elif "dasha" in question or "period" in question:
        return "Parasara Jyotish uses the Vimshottari Dasha system to time events. This system divides life into planetary periods (dashas) and sub-periods (antardashas). The sequence is: Sun (6 years), Moon (10 years), Mars (7 years), Rahu (18 years), Jupiter (16 years), Saturn (19 years), Mercury (17 years), Ketu (7 years), and Venus (20 years)."
    else:
        return "According to Parasara Jyotish principles, your question relates to the cosmic influences that shape our experiences. The planetary positions and their aspects form unique patterns that can provide insights into various life situations. Would you like to know more about a specific area of Vedic astrology?"

# Direct implementation of chat endpoints
@app.route('/api/chat/query', methods=['POST'])
def direct_chat_query():
    """Direct implementation of chat query endpoint that uses RAG"""
    logger.info("Chat query endpoint called")
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
        topic = data.get('topic')  # Get topic if provided
        
        logger.info(f"Processing message: {user_message[:30]}...")
        if topic:
            logger.info(f"Topic specified: {topic}")
        
        # Check for authentication
        current_user_id = handle_auth_optional_request()
        
        # If authenticated and conversation ID provided, use existing conversation
        if current_user_id and conversation_id and not conversation_id.startswith('direct-'):
            try:
                # Verify conversation exists and belongs to the user
                conversations_collection = get_conversations_collection()
                conversation = conversations_collection.find_one({
                    "_id": ObjectId(conversation_id),
                    "user_id": ObjectId(current_user_id)
                })
                
                if conversation:
                    # Get conversation history
                    messages_collection = get_messages_collection()
                    messages_cursor = messages_collection.find({
                        "conversation_id": conversation_id
                    }).sort("timestamp", 1)
                    
                    history = list(messages_cursor)
                    
                    # Get birth details from conversation if not provided
                    if not birth_details:
                        birth_details = conversation.get('birth_details', {})
                    
                    # Generate response using RAG
                    response_text = generate_response_with_rag(user_message, history, birth_details, topic)
                    
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
                else:
                    logger.warning(f"Conversation {conversation_id} not found or does not belong to user {current_user_id}")
            except Exception as e:
                logger.error(f"Error in authenticated conversation flow: {str(e)}")
                # Continue to fallback flow
        
        # For unauthenticated users or fallback
        logger.info("Using RAG for direct query flow")
        response_text = generate_response_with_rag(user_message, conversation_history, birth_details, topic)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'conversation_id': conversation_id or f'direct-{datetime.utcnow().timestamp()}'
        }), 200
        
    except Exception as e:
        logger.error(f"Chat query error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process query',
            'details': str(e)
        }), 500

@app.route('/api/chat/start', methods=['POST'])
def direct_start_conversation():
    """Direct implementation of start conversation endpoint"""
    logger.info("Start conversation endpoint called")
    try:
        # Get request data
        data = request.json or {}
        
        # Extract birth details
        birth_details = data.get('birth_details', {})
        
        # Check for authentication
        current_user_id = handle_auth_optional_request()
        
        # Generate welcome message
        welcome_message = "Welcome to Parasara Jyotish consultation! I'm your astrological assistant. Before we begin, could you please tell me a little about yourself?"
        
        # Create conversation in MongoDB if authenticated
        conversation_id = None
        if current_user_id:
            try:
                conversations_collection = get_conversations_collection()
                messages_collection = get_messages_collection()
                
                # Create conversation document
                current_time = datetime.utcnow()
                conversation_result = conversations_collection.insert_one({
                    "user_id": ObjectId(current_user_id),
                    "created_at": current_time,
                    "last_updated": current_time,
                    "birth_details": birth_details
                })
                
                conversation_id = str(conversation_result.inserted_id)
                
                # Store welcome message
                messages_collection.insert_one({
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": welcome_message,
                    "timestamp": current_time
                })
                
                logger.info(f"Created new conversation with ID {conversation_id} for user {current_user_id}")
            except Exception as e:
                logger.error(f"Error creating conversation: {str(e)}")
                conversation_id = f'direct-{datetime.utcnow().timestamp()}'
        else:
            conversation_id = f'direct-{datetime.utcnow().timestamp()}'
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'initial_response': welcome_message
        }), 200
    except Exception as e:
        logger.error(f"Start conversation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to start conversation',
            'details': str(e)
        }), 500

# Standard routes
@app.route('/')
def index():
    return jsonify({'message': 'Parasara Jyotish API is running'}), 200

@app.route('/api/health')
def health_check():
    try:
        get_db().command('ping')
        mongodb_status = "connected"
    except Exception as e:
        mongodb_status = f"error: {str(e)}"
    
    return jsonify({
        'status': 'healthy',
        'mongodb': mongodb_status,
        'version': flask.__version__,
        'vector_store': "available" if HAS_VECTOR_STORE else "unavailable"
    }), 200

# Register other blueprints
try:
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    logger.info("Registered auth and user blueprints")
except ImportError as e:
    logger.error(f"Error importing blueprints: {e}")

if __name__ == '__main__':
    # Verify MongoDB connection
    try:
        db = get_db()
        db.command('ping')
        logger.info("MongoDB connection successful")
        
        # Create required collections if they don't exist
        collections = db.list_collection_names()
        if "conversations" not in collections:
            db.create_collection("conversations")
            logger.info("Created 'conversations' collection")
        if "messages" not in collections:
            db.create_collection("messages")
            logger.info("Created 'messages' collection")
            
        # Test vector store if available
        if HAS_VECTOR_STORE:
            try:
                from vector_store import count_documents
                doc_count = count_documents()
                logger.info(f"Vector store contains {doc_count} documents")
            except Exception as e:
                logger.error(f"Error accessing vector store: {str(e)}")
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
