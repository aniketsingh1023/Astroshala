import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

astrology_system_message = """
You are an assistant to an Astrologer. Your task is to summarize and provide relevant astrological insights based on the provided context.

User input will include the necessary astrological context for you to answer their questions. This context will begin with the token: ###Context.
The context will contain references to specific astrological charts, planetary alignments, and zodiac sign traits relevant to the user's query.

Here is an example of how to structure your response:

Answer:
[Answer]

Source:
[Source information]
"""

def generate_response(context, question):
    """Generate a response using OpenAI API"""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": astrology_system_message},
                {"role": "user", "content": f"###Context\n{context}\n\n###Question\n{question}"}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f'Sorry, I encountered the following error: \n {e}'