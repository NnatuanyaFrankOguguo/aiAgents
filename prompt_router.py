from datetime import datetime
from openai import OpenAI
import os
import logging
from validators import EventConfirmation, EventExtraction, EventDetails, EventConfirmation


# Set up logging configuration so it can display logs in the terminal or interactive mode
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

# --------------------------------------------------------------
# Step 2: Define the functions for handling the agent reasoning logic thru openai api model
# --------------------------------------------------------------

def extract_event_info(user_input: str) -> EventExtraction:
    """First LLM call: to Extracts event information from user input to determine if its an event or not."""
    logger.info("Extracting event information...")
    logger.debug(f"Input text: {user_input}")

    today = datetime.now() # Get the current date and time incase the puts today it starts from today to count
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Analyze if the text describes a calendar event.",   
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        response_format=EventExtraction,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Extraction complete - is calender event: {result.is_calendar_event}, Confidence: {result.confidence_score:.2f}"
    )
    return result

