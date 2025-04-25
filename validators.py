from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
from datetime import datetime

# --------------------------------------------------------------
# Step 1: Define the data models for each stage
# --------------------------------------------------------------

class EventExtraction(BaseModel):
    """ First LLM call: Extract basic event information """

    description: str = Field(description="The raw description of the event.")
    is_calendar_event: bool = Field(description="Whether the event is a calendar event or not.")
    confidence_score : float = Field(description="The confidence score of the event between 0 and 1.")


class EventDetails(BaseModel):
    """Second LLM call: Parse Specific event details"""

    name: str = Field(description="The name of the event.")
    date: str = Field(description="Date and time of the event. Use ISO 8601 to format this value.")
    duration_minutes: int = Field(description="Expected duration in minutes")
    participants: list[str] = Field(description="List of participants")
    location: Optional[str] = Field(description="Location of the event (whether zoom or physical).")

    @field_validator('participants')
    @classmethod
    def validate_participants(cls, participants):
        if not participants:
            raise ValueError("At least one participant is required.")
        return participants
    
class EventConfirmation(BaseModel):
    """ Third LLM call: Confirm the event details """

    confirmation_message: str = Field(description="Natural language confirmation message.")

