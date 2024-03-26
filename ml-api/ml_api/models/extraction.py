from typing import List

from pydantic import BaseModel


class Actor(BaseModel):
    """
    Represents the information of a geopolitical actor. TODO consult with Dan about what fields to include
    """

    name: str
    actor_type: str
    goals: List[str]


class Location(BaseModel):
    """
    Represents the information of a location. TODO consult with Dan about what fields to include
    """

    name: str
    location_type: str
    description: str
