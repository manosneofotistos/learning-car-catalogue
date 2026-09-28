#Checkpoint 10: separate routes from application startup.
"""Define the API endpoints and translate database results into HTTP responses."""

from typing import Annotated #CHECKPOINT 11

from fastapi import APIRouter, HTTPException, Query, Response #CHECKPOINT 10: ALL - QUERY, CHECKPOINT 11: QUERY

from . import db
from .models import Category, Car, CarInput, ShortlistInput #CHECKPOINT 10: CarInput, CHECKPOINT 11: ELSE, 13: ShortlistInput


# Every endpoint registered on this router starts with /api.
# The tag groups these endpoints in the interactive documentation.
router = APIRouter(prefix="/api", tags=["Catalogue"])


@router.get("/health")
def health():
    """Confirm that the application can respond."""
    return {"status": "ok"}

# CHECKPOINT 10
# @router.get("/cars")
# def list_cars(q: str = "", category: str | None = None):
#     """Read matching cars from the database."""
#     return db.list_cars(q=q, category=category)

# CHECKPOINT 11 — Validate filters and describe the returned collection.
@router.get("/cars", response_model=list[Car])
def list_cars(
    q: Annotated[
        str,
        Query(
            max_length=100,
            description="Search the name, manufacturer, or description.",
        ),
    ] = "",
    category: Category | None = None,
):
    """Return cars matching the validated query parameters."""
    return db.list_cars(q=q, category=category)

# @router.get("/cars/{car_id}") - CHECKPOINT 10
@router.get("/cars/{car_id}", response_model=Car) # CHECKPOINT 11
def get_car(car_id: int):
    """Return one car, or HTTP 404 when its ID is missing."""
    car = db.get_car(car_id)

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="This car does not exist.",
        )

    return car


#@router.post("/cars", status_code=201) - CHECKPOINT 10
@router.post("/cars", status_code=201, response_model=Car) # CHECKPOINT 11
def create_car(data: CarInput):
    """Create a car using validated request content."""
    # FastAPI has validated the body; SQL helpers receive ordinary Python values.
    return db.create_car(data.model_dump())


#@router.put("/cars/{car_id}") - CHECKPOINT 10
@router.put("/cars/{car_id}", response_model=Car) # CHECKPOINT 11
def update_car(car_id: int, data: CarInput):
    """Replace the editable content of an existing car."""
    car = db.update_car(car_id, data.model_dump())

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="This car does not exist.",
        )

    return car


@router.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    """Delete a car and return an empty success response."""
    deleted = db.delete_car(car_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="This car does not exist.",
        )

    return Response(status_code=204)

# CHECKPOINT 13 — Read and modify the one shared shortlist.
@router.get("/shortlist", response_model=list[Car])
def list_shortlist():
    """Return cars saved by anyone using this shared demo."""
    return db.list_shortlist()

# CHECKPOINT 13 — Read and modify the one shared shortlist.
@router.put("/cars/{car_id}/shortlist", response_model=Car)
def set_shortlisted(car_id: int, data: ShortlistInput):
    """Set a car's saved state without changing its content."""
    # This boolean sets a state, so repeating the request preserves that state.
    car = db.set_shortlisted(car_id, data.shortlisted)

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="This car does not exist.",
        )

    return car