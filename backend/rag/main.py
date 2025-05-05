# main.py
import os
import logging
from pdf_processor import load_and_split_pdfs
from vector_store import create_vector_store, get_vector_store
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def process_pdfs():
    """Process PDFs and create vector store"""
    logger.info("Loading and processing PDFs...")
    text_chunks = load_and_split_pdfs()
    
    if not text_chunks:
        logger.warning("No PDF chunks found. Check your PDF directory.")
        return False
        
    logger.info(f"Successfully processed {len(text_chunks)} text chunks from PDFs")
    
    logger.info("Creating vector store...")
    success = create_vector_store(text_chunks)
    
    if success:
        logger.info("Vector store created successfully")
    else:
        logger.error("Failed to create vector store")
        
    return success

def generate_response(context, question):
    """Generate a response using OpenAI directly"""
    try:
        logger.info(f"Generating response for question: '{question[:50]}...'")
        
        # Create messages for the API
        messages = [
            {"role": "system", "content": "You are an expert Vedic astrologer specializing in Parasara Jyotish. Your task is to provide insightful and accurate responses based on the provided context."},
            {"role": "user", "content": f"Based on the following context, answer this question: {question}\n\nContext: {context}"}
        ]
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.5,
            max_tokens=500
        )
        
        # Extract the response content
        response_text = response.choices[0].message.content.strip()
        return response_text
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"Sorry, I encountered an error while generating a response: {str(e)}"

def test_rag_model(query="What are the 5 major planets in astrology?"):
    """Test the RAG model with a query"""
    logger.info(f"Testing RAG model with query: '{query}'")
    
    logger.info("Retrieving vector store...")
    vector_store = get_vector_store()
    
    if not vector_store:
        logger.error("Failed to load vector store. Make sure to run process_pdfs() first.")
        return "Error: Vector store not found"
    
    logger.info("Performing similarity search...")
    documents = vector_store.similarity_search(query, k=5)
    
    if not documents:
        logger.warning("No relevant documents found for the query")
        return "No relevant information found"
    
    logger.info(f"Found {len(documents)} relevant documents")
    
    # Extract and combine context
    context_list = [doc["page_content"] for doc in documents]
    context_for_query = " ".join(context_list)
    
    logger.info("Generating AI response...")
    response = generate_response(context_for_query, query)
    
    return response

def main():
    # Check if vector store exists
    if not os.path.exists("document_embeddings.pkl") or not os.path.exists("documents.pkl"):
        logger.info("Vector store not found. Creating new vector store...")
        process_pdfs()
    
    # Test queries
    queries = [
        "What are the 5 major planets in astrology?",
        "How does the Moon affect us in Vedic astrology?",
        "What is the significance of houses in a birth chart?",
        "How do planetary transits work?"
    ]
    
    for query in queries:
        response = test_rag_model(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response}")
        print("-" * 80)

if __name__ == "__main__":
    main()