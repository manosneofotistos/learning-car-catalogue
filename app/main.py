# # CHECKPOINT 1 - HTTP method GET and the path /api/health
# # CHECKPOINT 2 — List every car without filtering (GET METHOD).
# # CHECKPOINT 3 — Filter the collection using optional query parameters (GET METHOD).
# # CHECKPOINT 4 — Accept validated content and create a car (POST METHOD).
# # CHECKPOINT 5 — Replace the editable content of an existing car & Remove a Car. (PUT & DELETE)
# # CHECKPOINT 6 — store and retrieve a place in SQLite.
# # CHECKPOINT 7 — Create the application database and seed (seed.json) it. 
# # CHECKPOINT 8 — make the API read from SQLite.
# # CHECKPOINT 9 — Create, edit, and delete cars in SQLite.
# CHECKPOINT 10 — Assemble the application and register its API router.

# from fastapi import FastAPI, HTTPException, Response # FastAPI: CHECKPOINT 1, HTTPException: CHECKPOINT 2, Response: CHECKPOINT 5
# from .models import CarInput # CHECKPOINT 4

# # CHECKPOINT 1
# # Uvicorn will import this object to run our application.
# app = FastAPI(title="Car Catalogue API")

# # CHECKPOINT 2
# # Start with ordinary Python data so we can learn the API behavior first.
# # Later, our database will supply these records.
# CARS = [
#     {
#         "id": 1,
#         "name": "Toyota Corolla",
#         "category": "Hatchback",
#         "manufacturer": "Toyota",
#         "variant": "1.8 Hybrid Design",
#         "description": (
#             "A compact hybrid hatchback with supportive seats, "
#             "easy controls, and a quiet cabin for everyday driving."
#         ),
#         "tip": "Try the hybrid system in slow traffic during a test drive.",
#     },
#     {
#         "id": 2,
#         "name": "Volvo XC60",
#         "category": "SUV",
#         "manufacturer": "Volvo",
#         "variant": "B5 Plus AWD",
#         "description": (
#             "A comfortable SUV with a spacious cabin. Take a drive "
#             "to explore the visibility and relaxed driving position."
#         ),
#         "tip": "Check the rear seats and boot space before a test drive.",
#     },
#     {
#         "id": 3,
#         "name": "Toyota GR86",
#         "category": "Coupe",
#         "manufacturer": "Toyota",
#         "variant": "2.4 Boxer Manual",
#         "description": (
#             "A compact sports coupe with responsive steering and a set "
#             "of simple controls designed around the driver."
#         ),
#         "tip": "Try the manual gearbox on a varied test-drive route.",
#     },
# ]

# #CHECKPOINT 1
# # Connect the HTTP method GET and the path /api/health to this function.
# @app.get("/api/health")
# def health():
#     '''Confirm that the application can respond to a request.'''
#     # FastAPI converts this Python dictionary into a JSON response.
#     return {"status": "ok"}

# # CHECKPOINT 2
# @app.get("/api/cars")
# def list_cars():
#     """Return every car in the catalogue."""
#     # FastAPI converts a Python list of dictionaries into a JSON array.
#     return CARS

# # CHECKPOINT 3 — Filter the collection using optional query parameters.
# @app.get("/api/cars")
# def list_cars(q: str = "", category: str | None = None):
#     """Return cars matching the supplied search text and category."""
#     # Ignore accidental surrounding spaces and differences in letter case.
#     search_text = q.strip().casefold()

#     # Build a result list without changing our original collection.
#     matching_cars = []

#     for car in CARS:
#         # When a category is supplied, exclude cars in other categories.
#         if category is not None and car["category"] != category:
#             continue

#         # Search these three fields together.
#         searchable_text = " ".join(
#             [
#                 car["name"],
#                 car["manufacturer"],
#                 car["description"],
#             ]
#         ).casefold()

#         # An empty search means "do not restrict the results by text".
#         if search_text and search_text not in searchable_text:
#             continue

#         # This car passed every supplied filter.
#         matching_cars.append(car)

#     return matching_cars

# #CHECKPOINT 2
# @app.get("/api/cars/{car_id}")
# def get_car(car_id: int):
#     """Return one car, or respond with 404 if its ID does not exist."""
#     # The value from the URL arrives here as an integer.
#     for car in CARS:
#         if car["id"] == car_id:
#             return car

#     # Reaching this line means we checked every car without finding a match.
#     # Raise an HTTP error instead of returning a successful response with no data.
#     raise HTTPException(
#         status_code=404,
#         detail="This car does not exist.",
#     )

# # CHECKPOINT 4 — Accept validated content and create a car.
# @app.post("/api/cars", status_code=201)
# def create_car(data: CarInput):
#     """Create a car in our temporary in-memory collection."""
#     # Use an ID above every existing ID.
#     # The default handles an empty collection, where the first ID becomes 1.
#     next_id = max(
#         (car["id"] for car in CARS),
#         default=0,
#     ) + 1

#     # Convert the validated Pydantic object into an ordinary dictionary.
#     new_car = data.model_dump()

#     # The server supplies the identity after validating the client's content.
#     new_car["id"] = next_id

#     # This changes the running process's list, not the source file on disk.
#     CARS.append(new_car)

#     return new_car

# # CHECKPOINT 5 — Replace the editable content of an existing car.
# @app.put("/api/cars/{car_id}")
# def update_car(car_id: int, data: CarInput):
#     """Replace a car's content while preserving its ID."""
#     # enumerate() gives us both the list position and the car at that position.
#     for index, car in enumerate(CARS):
#         if car["id"] == car_id:
#             # Reuse the same validation rules as the create endpoint.
#             updated_car = data.model_dump()

#             # Editing content does not change the record's identity.
#             updated_car["id"] = car_id

#             # Replace the existing dictionary rather than appending another one.
#             CARS[index] = updated_car

#             return updated_car

#     # Updating a missing car does not create one in this API.
#     raise HTTPException(
#         status_code=404,
#         detail="This car does not exist.",
#     )

# # CHECKPOINT 5 — Remove an existing car.
# @app.delete("/api/cars/{car_id}", status_code=204)
# def delete_car(car_id: int):
#     """Delete a car and return an empty success response."""
#     for index, car in enumerate(CARS):
#         if car["id"] == car_id:
#             # Remove the matching dictionary from the shared in-memory list.
#             del CARS[index]

#             # Return immediately: do not continue iterating after deletion.
#             # HTTP 204 means success with no response body.
#             return Response(status_code=204)

#     raise HTTPException(
#         status_code=404,
#         detail="This car does not exist.",
#     )

# # CHECKPOINT 8 — Serve cars from the SQLite database.

# from contextlib import asynccontextmanager

# from fastapi import FastAPI, HTTPException, Response # CHECKPOINT 8: FastAPI, HTTP, CHECKPOINT 9: Response

# from . import db

# from .models import CarInput


# @asynccontextmanager
# async def lifespan(application: FastAPI):
#     """Prepare the database before the application accepts requests."""
#     db.initialize()

#     # Startup is complete. FastAPI serves requests while execution is paused here.
#     yield

#     # Shutdown cleanup would go below yield if we needed it.
#     # Our database helpers already close their own connections.


# app = FastAPI(
#     title="Car Catalogue API",
#     lifespan=lifespan,
# )


# @app.get("/api/health")
# def health():
#     """Confirm that the application can respond."""
#     return {"status": "ok"}


# @app.get("/api/cars")
# def list_cars(q: str = "", category: str | None = None):
#     """Read matching cars from the application database."""
#     return db.list_cars(q=q, category=category)


# @app.get("/api/cars/{car_id}")
# def get_car(car_id: int):
#     """Read one car and translate a missing record into HTTP 404."""
#     car = db.get_car(car_id)

#     if car is None:
#         raise HTTPException(
#             status_code=404,
#             detail="This car does not exist.",
#         )

#     return car

# # CHECKPOINT 9 — Connect validated HTTP requests to database writes.
# @app.post("/api/cars", status_code=201)
# def create_car(data: CarInput):
#     """Validate the request, create a car, and return its stored content."""
#     # Pass plain data to the database layer.
#     return db.create_car(data.model_dump())


# @app.put("/api/cars/{car_id}")
# def update_car(car_id: int, data: CarInput):
#     """Replace an existing car's editable content."""
#     car = db.update_car(car_id, data.model_dump())

#     if car is None:
#         raise HTTPException(
#             status_code=404,
#             detail="This car does not exist.",
#         )

#     return car


# @app.delete("/api/cars/{car_id}", status_code=204)
# def delete_car(car_id: int):
#     """Delete a car and return an empty success response."""
#     deleted = db.delete_car(car_id)

#     if not deleted:
#         raise HTTPException(
#             status_code=404,
#             detail="This car does not exist.",
#         )

#     return Response(status_code=204)

# CHECKPOINT 10 — Assemble the application and register its API router.

from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import db
from .routes import router

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize the database before accepting requests."""
    # Startup prepares persistence before any endpoint receives a request.
    db.initialize()
    # Execution pauses here while the application handles requests.
    yield


app = FastAPI(
    title="Car Catalogue API",
    lifespan=lifespan,
)

# Make the router's endpoints available through this application.
app.include_router(router)
