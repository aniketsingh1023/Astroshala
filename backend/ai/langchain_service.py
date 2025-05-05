# services/langchain_service.py
from langchain_openai import ChatOpenAI # type: ignore
from langchain.chains import LLMChain # type: ignore
from langchain.prompts import ( # type: ignore
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory # type: ignore
import os
import logging

logger = logging.getLogger(__name__)

class AstrologicalChatService:
    def __init__(self):
        try:
            # Initialize OpenAI chat model
            self.chat = ChatOpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                model_name="gpt-3.5-turbo",
                temperature=0.7
            )
            
            # Create prompt template using ChatPromptTemplate
            self.prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(
                    "You are an expert Parasara Jyotish astrologer with deep knowledge of Vedic astrology."
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}")
            ])

            # Initialize memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )

            # Create conversation chain
            self.conversation = LLMChain(
                llm=self.chat,
                prompt=self.prompt,
                memory=self.memory,
                verbose=True
            )

            logger.info("AstrologicalChatService initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AstrologicalChatService: {str(e)}")
            raise

    def generate_daily_horoscope(self, birth_details):
        """Generate daily horoscope based on birth details"""
        try:
            # Format birth details for the prompt
            input_text = f"""Based on the following birth details:
            Date: {birth_details.get('date')}
            Time: {birth_details.get('time')}
            Place: {birth_details.get('place')}
            
            Please provide a detailed daily horoscope analysis covering career, relationships, health, and general outlook."""

            # Generate response
            response = self.conversation.predict(input=input_text)
            return response

        except Exception as e:
            logger.error(f"Error generating horoscope: {str(e)}")
            return "Unable to generate horoscope at this time."

    def get_astro_guidance(self, question: str, birth_details: dict = None):
        """Get astrological guidance for specific questions"""
        try:
            input_text = question
            if birth_details:
                input_text = f"""Birth Details:
                Date: {birth_details.get('date')}
                Time: {birth_details.get('time')}
                Place: {birth_details.get('place')}
                
                Question: {question}"""

            response = self.conversation.predict(input=input_text)
            return response

        except Exception as e:
            logger.error(f"Error getting guidance: {str(e)}")
            return "Unable to provide guidance at this time."

    def clear_conversation_history(self):
        """Clear the conversation history"""
        try:
            self.memory.clear()
            logger.info("Conversation history cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing conversation history: {str(e)}")

    def start_new_conversation(self, user_id: str, initial_context: dict = None):
        """Start a new conversation with initial context"""
        try:
            # Clear existing conversation history
            self.clear_conversation_history()
            
            # If there's initial context, use it to start the conversation
            if initial_context:
                birth_details = initial_context.get('birth_details', {})
                if birth_details:
                    initial_prompt = f"""I am starting a new consultation with these birth details:
                    Date: {birth_details.get('date')}
                    Time: {birth_details.get('time')}
                    Place: {birth_details.get('place')}
                    
                    Please provide an initial astrological insight."""
                    
                    initial_response = self.conversation.predict(input=initial_prompt)
                    return {
                        'conversation_id': str(user_id),
                        'initial_response': initial_response
                    }
            
            # Default welcome message if no context
            initial_response = self.conversation.predict(
                input="I would like an astrological consultation."
            )
            return {
                'conversation_id': str(user_id),
                'initial_response': initial_response
            }

        except Exception as e:
            logger.error(f"Error starting new conversation: {str(e)}")
            return {
                'conversation_id': str(user_id),
                'initial_response': "I'm ready to begin our astrological consultation."
            }

    def analyze_birth_chart(self, birth_details: dict):
        """Analyze birth chart and provide insights"""
        try:
            input_text = f"""Please analyze the following birth chart details:
            Date: {birth_details.get('date')}
            Time: {birth_details.get('time')}
            Place: {birth_details.get('place')}
            
            Provide a comprehensive Vedic astrological analysis including:
            1. Major planetary positions and their influences
            2. Current dasha/antardasha periods
            3. Key strengths and challenges
            4. Recommendations for spiritual practices"""

            response = self.conversation.predict(input=input_text)
            return response

        except Exception as e:
            logger.error(f"Error analyzing birth chart: {str(e)}")
            return "Unable to analyze birth chart at this time."