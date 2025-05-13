# %%
from datetime import datetime
from openai import OpenAI
from typing import  Optional
import os
import logging
from validators import EventConfirmation, CalendarRequestType, EventDetails, EventConfirmation, CalendarResponse, ModifyEventDetails

# %%
# Set up logging configuration so it can display logs in the terminal or interactive mode
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

# %%
def determine_calendar_request_type(user_input: str) -> CalendarRequestType:
    """First LLM call: to determine the type of calendar request"""
    logger.info("Determining calendar request type...")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI agent. Your job is to classify user intents into categories like new_event, modify an existing event, etc."
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        response_format=CalendarRequestType
    )
    result = completion.choices[0].message.parsed
    logger.info(f"Calendar request type determined successfully: {result.request_type}, confidence: {result.confidence_score:.2f}")
    return result
# %%
def handle_new_event(description: str) -> CalendarResponse:
    """Second LLM call: to Parse(Extract) Specific event details."""
    logger.info("starting Parsing event details...")

    #Get the Event Details
    today = datetime.now() # Get the current date and time incase the puts today it starts from today to count
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract detailed event information. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference.",
            },
            {
                "role": "user",
                "content": description,
            }
        ],
        response_format=EventDetails,
    )
    details = completion.choices[0].message.parsed

    logger.info(f"Parsed event details - name: {details.name}, date: {details.date}, duration: {details.duration_minutes} minutes, participants: {details.participants}, location: {details.location}")
    logger.info(f"New event: {details.model_dump_json(indent=2)}")

    # Generate response to send to user
    return CalendarResponse(
        sucess=True,
        confirmation_message=f"Create new event '{details.name}' for {details.date} with {', '.join(details.participants)} .",
        calender_link=f"calendar://new?event={details.name}",
    )

# %%
def handle_modify_event(description: str) -> CalendarResponse:
    """Second LLM call: to Parse(Extract) Specific event details."""
    logger.info("processing event modification request...")

    #Get modification Details
    today = datetime.now() # Get the current date and time incase the puts today it starts from today to count
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract detailed for modifying an existing event information. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference ",
            },
            {
                "role": "user",
                "content": description,
            }
        ],
        response_format=ModifyEventDetails,
    )

    details = completion.choices[0].message.parsed

    logger.info(f"modified event details - name: {details.name}, date: {details.date}, duration: {details.duration_minutes} minutes, participants: {details.participants}, location: {details.location}")
    logger.info(f"Modified event: {details.model_dump_json(indent=2)}")

    # Generate response to send to user
    return CalendarResponse(
        sucess=True,
        confirmation_message=f"Modify event '{details.name}' for {details.date} with {', '.join(details.participants)} .",
        calender_link=f"calendar://modify?event={details.event_identifier}"
    )

# %%
def process_calendar_request(user_input: str) -> Optional[CalendarResponse]:
    """Main Function for implenting the routing workflow"""
    logger.info("Processing calendar request...")

    # Route the request
    route_result = determine_calendar_request_type(user_input)

    # check the confidence threshold
    if route_result.confidence_score < 0.7:
        logger.warning(f"Confidence score too low: {route_result.confidence_score:.2f}")
        return None
    
    # Route to appropriate handler
    if route_result.request_type == "new_event":
        return handle_new_event(route_result.description)
    elif route_result.request_type == "modify_event":
        return handle_modify_event(route_result.description)
    else:
        logger.warning("Request type not supported")
        return None

# --------------------------------------------------------------
# Step 3: Test with new event
# --------------------------------------------------------------

# %%
new_even_input = "Let's schedule a team meeting next Tuesday at 2pm with Alice alicemickal@gmail.com and Bob bobmars@gmail.com"

result = process_calendar_request(new_even_input)
if result:
    print(f"Response: {result.message}")






















































    # Process the request based on the determined type

# --------------------------------------------------------------
# Step 2: Define the functions for handling the agent reasoning logic thru openai api model
# --------------------------------------------------------------

#SINCE I COMMENTED THE EXTRACT FUNCTION BASEMODEL I DONT NEED THIS ITS REPLACED BY CALENDERREQUESTTYPE
# def extract_event_info(user_input: str) -> EventExtraction:
#     """First LLM call: to Extracts event information from user input to determine if its an event or not."""
#     logger.info("Extracting event information...")
#     logger.debug(f"Input text: {user_input}")

#     today = datetime.now() # Get the current date and time incase the puts today it starts from today to count
#     date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

#     completion = client.beta.chat.completions.parse(
#         model=model,
#         messages=[
#             {
#                 "role": "system",
#                 "content": f"{date_context} Analyze if the text describes a calendar event.",   
#             },
#             {
#                 "role": "user",
#                 "content": user_input
#             }
#         ],
#         response_format=EventExtraction,
#     )
#     result = completion.choices[0].message.parsed
#     logger.info(
#         f"Extraction complete - is calender event: {result.is_calendar_event}, Confidence: {result.confidence_score:.2f}"
#     )
#     return result




# I WANT TO MAKE THE PARSE_EVENT_DETAILS FUNCTION AND THE CONFIRM_EVENT_DETAILS FUNCTION A SINGLE FUNCTION 
# SO NO NEED FOR TWO LLM CALLS AGAIN

# def parse_event_details(description: str) -> EventDetails:
#     """Second LLM call: to Parse(Extract) Specific event details."""
#     logger.info("starting Parsing event details...")

#     today = datetime.now() # Get the current date and time incase the puts today it starts from today to count
#     date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

#     completion = client.beta.chat.completions.parse(
#         model=model,
#         messages=[
#             {
#                 "role": "system",
#                 "content": f"{date_context} Extract detailed event information. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference.",
#             },
#             {
#                 "role": "user",
#                 "content": description,
#             }
#         ],
#         response_format=EventDetails,
#     )

#     result = completion.choices[0].message.parsed
#     logger.info(
#         f"Parsed event details - name: {result.name}, date: {result.date}, duration: {result.duration_minutes} minutes, participants: {result.participants}, location: {result.location}"
#     )
#     logger.debug(f"Participants: {', '.join(result.participants)}")
#     return result


# def confirm_event_details(event_details: EventDetails) -> EventConfirmation:
#     """Third LLM call: to Confirm the event details."""
#     logger.info("Confirming event details message...")

#     completion = client.beta.chat.completions.parse(
#         model=model,
#         messages=[
#             {
#                 "role": "system",
#                 "content": "Generate a natural language confirmation message for the event details. include a link to the calendar event if it is a calendar event. Use markdown formatting. sign off with your name; susie",
#             },
#             {
#                 "role": "user",
#                 "content": str(event_details.model_dump()),
#             }
#         ]
#     )
#     result = completion.choices[0].message.parsed
#     logger.info(f"Confirmation message generated successfully: {result.confirmation_message}")
#     logger.info(f"Calender link: {result.calender_link}")
#     return result


# %%
print(os.getenv("DEEPSEEK_API_KEY"))
# %%
