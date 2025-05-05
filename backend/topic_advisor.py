"""
Topic-specific astrological advisor module for the ASHTOSHALA project.
Handles specialized advice for career, relationships, and finances.
"""
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Topic-specific system prompts
CAREER_SYSTEM_PROMPT = """
You are an expert Vedic Astrology advisor specializing in **career and professional life**. 
Analyze the birth chart to provide specific insights on:

1. **Natural Career Talents**: Based on the 10th house (karma), 6th house (service), and key planets like Sun, Mars, Mercury, and Jupiter.

2. **Current Career Phase**: Analyze the current Mahadasha and Bhukti to explain:
   - Why the person might be experiencing current job situations
   - When favorable career shifts might occur
   - Which industries or roles align with planetary positions

3. **Professional Relationships**: How the person interacts with colleagues, superiors, and subordinates.

4. **Business vs. Employment**: Whether the person is better suited for entrepreneurship or employment.

5. **Timing for Career Moves**: Favorable periods for job changes, promotions, or starting businesses.

6. **Remedies for Career Growth**: Specific mantras, gemstones, or practices to enhance career prospects.

IMPORTANT: Keep your response concise and under 600 tokens (approximately 450 words). Focus on the most relevant insights.

Always provide practical, actionable advice that the person can implement. If birth details are incomplete, acknowledge the limitations in your analysis.

Use **bold** for sections, *italics* for key words, and space for readability.
"""

MARRIAGE_SYSTEM_PROMPT = """
You are an expert Vedic Astrology advisor specializing in **marriage and relationships**. 
Analyze the birth chart to provide specific insights on:

1. **Relationship Patterns**: Based on the 7th house (partnerships), Venus, Mars, and Moon positions.

2. **Current Relationship Phase**: Analyze the current Mahadasha and Bhukti to explain:
   - Why the person might be experiencing current relationship situations
   - When favorable relationship developments might occur
   - What relationship patterns are being activated

3. **Marriage Timing**: Potential periods for marriage or significant relationships.

4. **Partner Compatibility**: The type of partner who would be most compatible.

5. **Relationship Challenges**: Potential areas of conflict or growth in relationships.

6. **Remedies for Relationship Harmony**: Specific mantras, gemstones, or practices to enhance relationship prospects.

IMPORTANT: Keep your response concise and under 600 tokens (approximately 450 words). Focus on the most relevant insights.

Always provide practical, actionable advice that the person can implement. If birth details are incomplete, acknowledge the limitations in your analysis.

Use **bold** for sections, *italics* for key words, and space for readability.
"""

FINANCE_SYSTEM_PROMPT = """
You are an expert Vedic Astrology advisor specializing in **finance and wealth**. 
Analyze the birth chart to provide specific insights on:

1. **Wealth Potential**: Based on the 2nd house (wealth), 11th house (gains), and key planets like Jupiter, Venus, and Mercury.

2. **Current Financial Phase**: Analyze the current Mahadasha and Bhukti to explain:
   - Why the person might be experiencing current financial situations
   - When favorable financial developments might occur
   - Which wealth-building strategies align with planetary positions

3. **Income Sources**: Best sources of income based on planetary positions.

4. **Investment Guidance**: Types of investments that may be favorable.

5. **Financial Challenges**: Potential areas of financial risk or loss.

6. **Remedies for Financial Growth**: Specific mantras, gemstones, or practices to enhance wealth prospects.

IMPORTANT: Keep your response concise and under 600 tokens (approximately 450 words). Focus on the most relevant insights.

Always provide practical, actionable advice that the person can implement. If birth details are incomplete, acknowledge the limitations in your analysis.

Use **bold** for sections, *italics* for key words, and space for readability.
"""

def get_topic_prompt(topic):
    """Get the appropriate system prompt for a specific topic"""
    if topic == 'job':
        return CAREER_SYSTEM_PROMPT
    elif topic == 'marriage':
        return MARRIAGE_SYSTEM_PROMPT
    elif topic == 'finance':
        return FINANCE_SYSTEM_PROMPT
    else:
        logger.warning(f"Unknown topic: {topic}, using default prompt")
        return None

def generate_topic_response(openai_client, user_message, topic, conversation_history=None, birth_details=None):
    """Generate a topic-specific response using OpenAI"""
    try:
        # Get topic-specific system prompt
        topic_prompt = get_topic_prompt(topic)
        if not topic_prompt:
            logger.warning(f"No specific prompt for topic: {topic}")
            return f"I'd be happy to provide insights about your {topic}. To give you the most accurate guidance, I'll need to analyze your birth chart."
        
        # Build messages array for OpenAI
        messages = [{"role": "system", "content": topic_prompt}]
        
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
        else:
            messages.append({"role": "system", "content": "The user has not provided complete birth details. Acknowledge this limitation in your response and suggest that they provide their birth date, time, and place for a more accurate reading."})
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add the user message
        messages.append({"role": "user", "content": user_message})
        
        logger.info(f"Sending topic-specific request to OpenAI with {len(messages)} messages")
        
        # Get response from OpenAI with max_tokens set to 600
        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.7,
            max_tokens=600  # Limit to 600 tokens
        )
        
        response_text = response.choices[0].message.content
        logger.info(f"Received topic-specific response from OpenAI: {response_text[:50]}...")
        return response_text
    
    except Exception as e:
        logger.error(f"Error generating topic-specific response: {str(e)}")
        return f"I'd be happy to provide insights about your {topic}, but I encountered an error. Please try again or provide more details about what you'd like to know."

def generate_mock_topic_response(topic):
    """Generate a mock topic-specific response (fallback)"""
    if topic == 'job':
        return """
## Career & Professional Insights

Based on Vedic astrological principles, here are some insights about your career path:

**Natural Talents & Strengths**
Your chart suggests you have strong analytical abilities and communication skills. Mercury's position indicates you may excel in fields requiring detailed analysis, writing, or teaching.

**Current Career Phase**
You appear to be in a phase of professional growth and change. This is a good time to explore new opportunities in your field and develop new skills that align with your interests.

**Timing for Career Moves**
The next 6-8 months look particularly favorable for career advancement. Consider making important moves during this window.

**Remedies for Career Growth**
- Recite the Mercury mantra "Om Budhaya Namaha" 108 times on Wednesdays
- Wear a green or emerald stone (after proper consultation)

For a more detailed reading, please provide your complete birth details.
"""
    elif topic == 'marriage':
        return """
## Marriage & Relationship Insights

Based on Vedic astrological principles, here are some insights about your relationships:

**Relationship Patterns**
Your chart suggests you value emotional security and intellectual connection in relationships. Venus's position indicates you're attracted to partners who are both emotionally nurturing and mentally stimulating.

**Current Relationship Phase**
You appear to be in a phase of relationship reflection or transformation. This is a good time to evaluate what you truly need from partnerships.

**Compatibility Factors**
You likely connect well with partners who respect your need for independence and share your intellectual interests.

**Remedies for Relationship Harmony**
- Recite the Venus mantra "Om Shukraya Namaha" 108 times on Fridays
- Practice forgiveness meditation to release past relationship karma

For a more detailed reading, please provide your complete birth details.
"""
    elif topic == 'finance':
        return """
## Financial & Wealth Insights

Based on Vedic astrological principles, here are some insights about your financial situation:

**Wealth Potential**
Your chart suggests you have good potential for wealth accumulation, particularly through multiple income streams. Jupiter's position indicates potential for growth through investments.

**Current Financial Phase**
You appear to be in a phase of financial reorganization or planning. This is a good time to review your budget and consider new investment strategies.

**Income Sources**
You may find success in knowledge-based enterprises, financial services, or creative business models.

**Remedies for Financial Growth**
- Recite the Jupiter mantra "Om Gurave Namaha" 108 times on Thursdays
- Donate to educational or spiritual causes to enhance wealth karma

For a more detailed reading, please provide your complete birth details.
"""
    else:
        return f"I'd be happy to provide insights about your {topic}. To give you the most accurate guidance, I'll need to analyze your birth chart. Could you please share your birth details (date, time, and place of birth)?"
