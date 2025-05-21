# %%
from pydantic import BaseModel, field_validator, Field
from typing import  Optional, Literal
from datetime import datetime

# --------------------------------------------------------------
# Step 1: Define the data models for each stage
# --------------------------------------------------------------

# 1.1 CREATION AND CONFIRMATION OF EVENTS
# class EventExtraction(BaseModel):
#     """ First LLM call: Extract basic event information """

#     description: str = Field(description="The raw description of the event.")
#     is_calendar_event: bool = Field(description="Whether the event is a calendar event or not.")
#     confidence_score : float = Field(description="The confidence score of the event between 0 and 1.")

# %%
class Participant(BaseModel):
    name: str = Field(description="Name of the participant")
    email: str = Field(description="Email of the participant")

# %%
class EventDetails(BaseModel):
    """Second LLM call: Parse Specific event details"""

    name: str = Field(description="The name of the event.")
    date: str = Field(description="Date and time of the event. Use ISO 8601 to format this value.")
    duration_minutes: int = Field(description="Expected duration in minutes")
    participants: list[Participant] = Field(description="List of participants with name and email.")
    location: Optional[str] = Field(description="Location of the event (whether zoom or physical).")

    @field_validator('participants')
    @classmethod
    def validate_participants(cls, participants):
        if not participants:
            raise ValueError("At least one participant is required.")
        return participants

# %%
class EventConfirmation(BaseModel):
    """ Third LLM call: Confirm the event details """

    confirmation_message: str = Field(description="Natural language confirmation message.")
    calender_link: Optional[str] = Field(description="Link to the calendar event (generated calender link if applicable).")


# 1.2 RESCHEDULE OR MODIFY EVENT 
# %%
# 2nd validator flow
class CalendarRequestType(BaseModel):
    """Router LLM call: Determine the type of calendar request"""

    request_type: Literal["new_event", "modify_event", "other"] = Field(
        description="The type of calendar request being made."
    )
    confidence_score : float = Field(description="The confidence score of the event between 0 and 1.")
    description: str = Field(description="Cleaned description of the event request.")

# %%
# 1st validator flow
class CalendarValidation(BaseModel):
    """Router LLM call: Determine if the user input is a valid calendar event before checking if its a new calander event or modify an existing event"""

    is_calendar_event: bool = Field(description="Whether the user input is a calendar event or not.")
    confidence_score : float = Field(description="The confidence score of the event between 0 and 1.")
    #description: str = Field(description="Cleaned description of the event request.")

# %%
class SecurityCheck(BaseModel):
    """Check for prompt injection or system manipulation attempts"""

    is_safe: bool = Field(description="Whether the prompt is safe or not.")
    risk_flags: list[str] = Field(description="List of risk flags associated with the prompt.")
# %%
class Change(BaseModel):
    """Router LLM call: Determine the type of change (Details for change an existing event)"""

    field: str = Field(description="Field to change")
    new_value: str = Field(description="New value for the field")

# %%
class ModifyEventDetails(BaseModel):
    """Router LLM call: Details for modifying an existing event """

    event_identifier: str = Field(description="Description(Unique identifier) to identify the existing event.")
    changes: list[Change] = Field(description="List of changes to be made to the event.")
    participants_to_add: list[Participant] = Field(description="List of new participants to add (name and email).")
    participants_to_remove: list[str] = Field(description="List of participants to remove from the event.")
    date: Optional[datetime] = Field(description="New date and time for the event. Use ISO 8601 to format this value.")
    location: Optional[str] = Field(description="New location for the event (whether zoom or physical).")

    @field_validator('changes')
    @classmethod    
    def validate_changes(cls, changes):
        if not changes:
            raise ValueError("At least one change is required.")
        return changes
# %%  
# last response structured vaildator flow
class CalendarResponse(BaseModel):
    """Router LLM call: Confirm the modified event details """

    sucess: bool = Field(description="Whether the event was successfully modified or not.")
    confirmation_message: str = Field(description="Natural language confirmation message, user-friendly response message.")
    calender_link: Optional[str] = Field(description="Link to the calendar event (generated calender link if applicable).")

# then go to the prompt_router to define the routing processing
# %%
