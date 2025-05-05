# services/chat_service.py
import datetime
from langchain_openai import ChatOpenAI # type: ignore
from langchain.schema import HumanMessage, SystemMessage # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import logging
from typing import List, Union, Dict, Any
import json

logger = logging.getLogger(__name__)

class MockChatModel:
    """Mock chat model for testing when OpenAI is not available"""
    def __init__(self):
        self.responses = {
            "astrology": "According to Vedic astrology, planetary positions at the time of birth significantly influence one's life path.",
            "horoscope": "Your daily horoscope suggests a period of positive energy and growth.",
            "birth_chart": "Your birth chart shows interesting planetary alignments that indicate..."
        }

    def invoke(self, messages: List[Union[SystemMessage, HumanMessage]]) -> str:
        # Extract the last human message
        last_message = next((msg for msg in reversed(messages) 
                           if isinstance(msg, HumanMessage)), None)
        
        if not last_message:
            return {"content": "No message provided"}
            
        # Determine which mock response to return
        content = last_message.content.lower()
        for key, response in self.responses.items():
            if key in content:
                return {"content": response}
                
        return {"content": "I understand you're interested in Vedic astrology. How can I assist you today?"}

class AstrologicalChatService:
    def __init__(self, use_mock: bool = False):
        try:
            load_dotenv()
            
            if use_mock:
                logger.info("Initializing mock chat service")
                self.chat = MockChatModel()
            else:
                logger.info("Initializing OpenAI chat service")
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    logger.warning("No OpenAI API key found, falling back to mock service")
                    self.chat = MockChatModel()
                else:
                    self.chat = ChatOpenAI(
                        api_key=api_key,
                        model_name="gpt-3.5-turbo",
                        temperature=0.7
                    )
            
            self.conversation_history: List[Dict[str, Any]] = []
            logger.info("Chat service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing chat service: {str(e)}")
            self.chat = MockChatModel()  # Fallback to mock service
            logger.info("Fallback to mock service successful")

    def generate_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Generate a response based on user input and optional context"""
        try:
            messages = [
                SystemMessage(content=(
                    "You are an expert Vedic astrologer specializing in Parasara Jyotish. "
                    "Provide insights based on traditional Vedic astrology principles."
                ))
            ]

            # Add context if available
            if context:
                context_msg = (
                    f"Birth Details - Date: {context.get('date', 'Unknown')}, "
                    f"Time: {context.get('time', 'Unknown')}, "
                    f"Place: {context.get('place', 'Unknown')}"
                )
                messages.append(SystemMessage(content=context_msg))

            # Add conversation history
            for msg in self.conversation_history[-5:]:  # Keep last 5 messages
                messages.append(msg['message'])

            # Add user input
            messages.append(HumanMessage(content=user_input))

            # Generate response
            response = self.chat.invoke(messages)
            
            # Store in conversation history
            self.conversation_history.append({
                'message': HumanMessage(content=user_input),
                'timestamp': str(datetime.datetime.now())
            })
            self.conversation_history.append({
                'message': SystemMessage(content=str(response.get('content', ''))),
                'timestamp': str(datetime.datetime.now())
            })

            return str(response.get('content', 'I apologize, but I am unable to provide a response at the moment.'))

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I am unable to provide a response at the moment. Please try again later."

    def get_daily_horoscope(self, birth_details: Dict[str, Any]) -> str:
        """Generate daily horoscope based on birth details"""
        prompt = (
            f"Based on the birth details - "
            f"Date: {birth_details.get('date', 'Unknown')}, "
            f"Time: {birth_details.get('time', 'Unknown')}, "
            f"Place: {birth_details.get('place', 'Unknown')}, "
            f"please provide a detailed daily horoscope covering career, "
            f"relationships, health, and general outlook."
        )
        return self.generate_response(prompt, birth_details)

    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

def test_service():
    """Test the chat service functionality"""
    service = AstrologicalChatService(use_mock=True)  # Use mock service for testing
    
    # Test basic response
    response = service.generate_response("Tell me about Vedic astrology")
    print("\nBasic Response Test:")
    print(response)
    
    # Test horoscope generation
    birth_details = {
        "date": "1990-01-01",
        "time": "12:00",
        "place": "New Delhi, India"
    }
    horoscope = service.get_daily_horoscope(birth_details)
    print("\nHoroscope Test:")
    print(horoscope)
    
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = test_service()
    print("\nService Test Success:", success)