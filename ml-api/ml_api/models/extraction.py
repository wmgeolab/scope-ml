from typing import List

from pydantic.v1 import BaseModel, Field


class Actor(BaseModel):
    """
    Represents the information of a geopolitical actor. TODO consult with Dan about what fields to include
    """

    name: str = Field(description="The name of the actor")
    type: str = Field(description="The type of actor")
    goals: List[str] = Field(
        description="The specific goals or intentions of the actor"
    )


class Location(BaseModel):
    """
    Represents the information of a location.
    """

    name: str = Field(description="The name of the location.")
    type: str = Field(description="The type of location.")
    description: str = Field(description="A description of the location.")


class ExtractedLocations(BaseModel):
    """
    Represents the extracted locations from a document.
    """

    locations: List[Location] = Field(
        description="The locations extracted from the document."
    )


class ExtractedActors(BaseModel):
    """
    Represents the extracted actors from a document.
    """

    actors: List[Actor]
