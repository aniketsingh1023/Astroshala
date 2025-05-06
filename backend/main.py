import os
import logging
import flask
from flask import Flask, jsonify, request
from flask_cors import CORS 
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Global handler for CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Global handler for OPTIONS requests
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return '', 200

# Configure MongoDB - using direct MongoClient instead of PyMongo
mongo_uri = os.getenv("MONGODB_URI")
if not mongo_uri:
    logger.error("MONGODB_URI is not set in .env")
    mongo_uri = "mongodb://localhost:27017/contact_details"  # Fallback for development

try:
    # Connect to MongoDB
    mongo_client = MongoClient(mongo_uri)
    # Test the connection
    mongo_client.admin.command('ping')
    logger.info("MongoDB connection successful")
    
    # Get the contact_details database
    db = mongo_client["contact_details"]
    
    # Check if the Contact collection exists, create if not
    if "Contact" not in db.list_collection_names():
        db.create_collection("Contact")
        logger.info("Created 'Contact' collection in 'contact_details' database")
        
except Exception as e:
    logger.error(f"MongoDB connection error: {str(e)}")
    mongo_client = None
    db = None

# JWT configuration
jwt_secret = os.getenv('JWT_SECRET')
if not jwt_secret:
    jwt_secret = "dev-secret-key"  # Fallback for development
    logger.warning("Using development JWT secret key")

app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

jwt = JWTManager(app)

# Initialize OpenAI client if API key is available
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
    logger.info("OpenAI client initialized")
else:
    openai_client = None
    logger.warning("OPENAI_API_KEY not set, AI features will be unavailable")

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
        # Get relevant documents from vector store if available
        context = ""
        if HAS_VECTOR_STORE:
            try:
                # Get vector database name from environment variables
                vector_db_name = os.getenv('VECTOR_DB_NAME', 'vector_db')
                vector_collection_name = os.getenv('VECTOR_COLLECTION_NAME', 'Vectors')
                
                relevant_documents = search_similar_pdfs(
                    user_message, 
                    top_k=5,
                    db_name=vector_db_name,
                    collection_name=vector_collection_name
                )
                
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
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.7,
            max_tokens=600  # Limit to 600 tokens
        )
        
        response_text = response.choices[0].message.content
        logger.info(f"Received response from OpenAI: {response_text[:50]}...")
        return response_text
    
    except Exception as e:
        logger.error(f"Error generating RAG response: {str(e)}")
        return generate_mock_response(user_message)

def generate_mock_response(question):
    """Generate a mock response based on the question (fallback)"""
    question = question.lower() if hasattr(question, 'lower') else question.lower()
    
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
        if mongo_client is not None:
            mongo_client.admin.command('ping')
            mongodb_status = "connected"
        else:
            mongodb_status = "not connected"
    except Exception as e:
        mongodb_status = f"error: {str(e)}"
    
    return jsonify({
        'status': 'healthy',
        'mongodb': mongodb_status,
        'version': flask.__version__
    }), 200

# Simple contact form submission endpoint
@app.route('/api/contact/direct-submit', methods=['POST'])
def direct_submit_contact():
    """Direct implementation of contact form submission"""
    try:
        # Get request data
        data = request.json
        logger.info(f"Received direct contact form submission: {data}")
        
        # Validate required fields
        required_fields = ['name', 'email', 'contactNumber', 'birthDate', 'birthTime', 'birthPlace']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Check if MongoDB is connected
        if mongo_client is None:
            logger.error("MongoDB client is None")
            return jsonify({
                'success': False,
                'error': 'Database connection error'
            }), 500
        
        # Format data for MongoDB
        contact_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'contactNumber': data.get('contactNumber'),
            'birthDate': data.get('birthDate'),
            'birthTime': data.get('birthTime'),
            'birthPlace': data.get('birthPlace'),
            'message': data.get('message', ''),
            'created_at': datetime.now().isoformat()
        }
        
        # Insert into MongoDB
        result = db["Contact"].insert_one(contact_data)
        logger.info(f"Contact form saved with ID: {result.inserted_id}")
        
        return jsonify({
            'success': True,
            'message': 'Form submitted successfully',
            'id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in direct contact form submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process contact form',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
