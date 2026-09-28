# CHECKPOINT 4 
"""Define the data clients must send when creating or editing a car."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# A category must match one of these strings exactly.
Category = Literal[
    "Hatchback",
    "Sedan",
    "SUV",
    "Coupe",
]


class CarInput(BaseModel):
    """The editable content of a car, without a server-generated ID."""

    model_config = ConfigDict(
        # Remove surrounding whitespace before checking string lengths.
        str_strip_whitespace=True,
        # Reject unexpected fields rather than silently ignoring them.
        extra="forbid",
    )

    # POST and PUT validate the same six editable fields.
    name: str = Field(min_length=2, max_length=80)
    category: Category
    manufacturer: str = Field(min_length=2, max_length=60)
    variant: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=20, max_length=1000)
    tip: str = Field(min_length=5, max_length=200)

# CHECKPOINT 11 — Describe a car returned by the API.
class Car(CarInput):
    """A stored car includes its content and its server-generated ID."""

    # Inheritance reuses the input rules; responses add the stored identity.
    id: int
    shortlisted: bool # CHECKPOINT 13
    
# CHECKPOINT 13 — Set a car's membership in the shared shortlist.
class ShortlistInput(BaseModel):
    """Accept an explicit saved or unsaved state."""

    model_config = ConfigDict(
        extra="forbid",
        # Require a JSON boolean, rather than accepting strings or numbers.
        strict=True,
    )

    shortlisted: bool