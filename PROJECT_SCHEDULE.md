# Project teaching schedule

## Lesson plan

Seven 90-minute lessons, following the checkpoints in order. The timings include explanation during demonstrations and room for discussion.

| Lesson | Checkpoints | What we show | Timing |
| --- | --- | --- | --- |
| **1. Requests, routes, and reading data** | **1–3** | Briefly demonstrate the finished catalogue in `/docs`. Build the health endpoint, in-memory car list, individual lookup, search, and category filters. Explain methods, paths, query parameters, JSON, and status codes as they appear. | 10 min preview; 20 min CP1; 20 min CP2; 20 min CP3; 20 min discussion and recap |
| **2. Validating and changing data** | **4–5** | Introduce `CarInput`, show accepted and rejected request bodies, then create, replace, and delete cars. Restart the server to show that in-memory changes disappear. | 10 min recap; 30 min CP4; 30 min CP5; 20 min discussion and recap |
| **3. Persistence and database initialization** | **6–7** | Work through the create, insert, and read SQLite scripts. Build the application schema, seed file, connection helper, and initializer. Run initialization twice and inspect the results. | 10 min recap; 25 min CP6; 40 min CP7; 15 min discussion |
| **4. Connecting HTTP to SQLite** | **8–9** | Trace a GET from route to SQL and back. Connect POST, PUT, and DELETE to database writes. Demonstrate persistence across restart and explain the responsibilities of routes and database helpers. | 10 min recap; 25 min CP8; 35 min CP9; 20 min discussion and recap |
| **5. Organizing the API and describing its contract** | **10–11** | Move handlers into a router while preserving behavior. Add response models and query validation. Compare request and response schemas in `/docs`, then demonstrate invalid filters. | 10 min recap; 25 min CP10; 30 min CP11; 25 min discussion and request tracing |
| **6. Relationships and the shared shortlist** | **12–13** | Draw the two tables and demonstrate membership directly in SQL, then expose it through the API. Explain joins, foreign keys, cascade deletion, and repeated saves that preserve the requested state. | 10 min recap; 30 min CP12; 35 min CP13; 15 min discussion |
| **7. Testing the complete backend** | **14** | Explain isolation and fixtures, then build the five tests progressively. Run each test and interpret its assertions. Temporarily break one behavior to demonstrate a meaningful failure, then restore it. | 10 min recap; 20 min fixtures; 40 min tests; 20 min discussion and connection to the student project |

Lesson 3 has the tightest timing: checkpoint 7 combines paths, context managers, transactions, schema execution, and the seed marker. Explain these by following execution: what opens, what runs, what commits, and what closes. If discussion needs more time, finish checkpoint 7 at the beginning of lesson 4 before proceeding to checkpoint 8.

## Checkpoint questions and model answers

Ask one question during the build and one at the checkpoint's end. Where possible, ask students to predict the result before executing the request or script. The model answers describe the understanding to listen for; students do not need to repeat the wording exactly.

### Checkpoint 1 — Respond to an HTTP request

**Question 1: What connects this URL to this Python function?**

**Model answer:** The route decorator registers the function for an HTTP method and path. A GET request to `/api/health` matches `@app.get("/api/health")`, so FastAPI calls that function. The method matters as well as the URL.

**Question 2: We return a dictionary—why does the client receive JSON?**

**Model answer:** FastAPI converts the returned Python dictionary into a JSON response. The client receives serialized data over HTTP, not the Python object itself.

### Checkpoint 2 — Read cars from a Python list

**Question 1: What is different about requesting an unknown integer ID and requesting `abc` as the ID?**

**Model answer:** An unknown integer passes the path-parameter validation, but our handler cannot find a matching car and raises 404. `abc` cannot satisfy `car_id: int`, so FastAPI rejects it with 422 before the handler searches the list.

**Question 2: Why is the missing-record error outside the loop?**

**Model answer:** We must check every car before concluding that the ID is missing. Raising the error on the first nonmatching car would stop the search even if a later car matched. A match returns immediately; reaching the end means none matched.

### Checkpoint 3 — Filter the collection

**Question 1: When both filters are supplied, must one match or both?**

**Model answer:** Both must match. A car must belong to the requested category and contain the search text in the combined searchable fields. Matching only one condition is not enough.

**Question 2: Does searching change the original collection?**

**Model answer:** No. The handler builds and returns a separate list of matching cars. It does not remove cars from `CARS`, so another request without filters can still return the full collection.

### Checkpoint 4 — Validate input and create a car

**Question 1: Who supplies the ID: the client or the server?**

**Model answer:** The server supplies it. The client sends the six editable fields. At this checkpoint, the handler calculates an ID above the existing IDs and adds it to the new dictionary. An `id` in the request body is rejected because `CarInput` forbids extra fields.

**Question 2: If validation fails, does the handler append anything to the list?**

**Model answer:** No. FastAPI validates the body against `CarInput` before calling the handler. Invalid input receives 422, so the append operation never runs and the collection is unchanged.

### Checkpoint 5 — Replace and delete a car

**Question 1: Why must PUT include fields that we aren't changing?**

**Model answer:** This API defines PUT as a complete replacement of editable content and validates it with the same `CarInput` model used for creation. All six fields are required. The server preserves the existing ID.

**Question 2: What should happen when we delete the same car twice?**

**Model answer:** The first request deletes the car and returns 204 with no body. The second finds no matching car and returns 404. The car remains absent; repeating the request does not delete a different record.

### Checkpoint 6 — Store and retrieve a car in SQLite

**Question 1: The insert script has finished. How can the read script still find its data?**

**Model answer:** The insert was committed to the SQLite file. Ending the process or closing the connection does not remove that committed data. The read script opens a new connection to the same file.

**Question 2: What happens if we run the insert script twice?**

**Model answer:** It inserts two rows with different generated IDs. The script performs an INSERT each time, and this table does not require car names or the other content fields to be unique. The create-table script does not clear previous rows.

### Checkpoint 7 — Create and seed the application database

**Question 1: Why do we record a seed marker instead of checking whether the cars table is empty?**

**Model answer:** An empty table might mean that someone intentionally deleted all cars. The marker records that initial seeding already happened, so restarting the application does not restore content the user deleted.

**Question 2: If inserting a seed record fails, should the earlier inserts and marker be committed?**

**Model answer:** No. The seed inserts and marker belong to one transaction. If an insert fails, earlier inserts in that transaction are rolled back, and no success marker is committed. The marker is written only after all seed inserts succeed.

### Checkpoint 8 — Read the database through HTTP

**Question 1: Which part decides that a missing record means HTTP 404?**

**Model answer:** The route makes that decision. The database helper returns `None` when no row matches, and the route turns that result into an `HTTPException` with status 404. The SQL helper does not need to handle HTTP responses.

**Question 2: Why are the search values passed separately from the SQL?**

**Model answer:** Placeholders let SQLite treat user input as data rather than SQL instructions. We build the query from fixed clauses and supply values separately, so quotes or SQL-looking text in a search do not change the query's structure.

### Checkpoint 9 — Create, edit, and delete in SQLite

**Question 1: Why read the created record using the same connection?**

**Model answer:** That connection can read its own insertion before the transaction commits. We use the INSERT cursor's `lastrowid` to select the exact row we created and return its stored content. A separate connection would not normally see that uncommitted insertion.

**Question 2: How do we distinguish an update that found its target from one that didn't?**

**Model answer:** We inspect the UPDATE cursor's `rowcount`. With this primary-key lookup, zero means no matching record, so the helper returns `None` and the route returns 404. A match lets us read and return the updated record. Submitting the same values again does not mean the record is missing.

### Checkpoint 10 — Separate routing from startup

**Question 1: What has changed for someone calling the API?**

**Model answer:** The existing request paths, methods, bodies, and behavior remain the same. We moved the handlers into `routes.py` and registered their router in `main.py`. The documentation now groups those operations under the `Catalogue` tag.

**Question 2: Where does the `/api` part of each path now come from?**

**Model answer:** It comes from `APIRouter(prefix="/api")`. The individual decorators use paths such as `/cars`. Keeping `/api` in those decorators as well would incorrectly produce `/api/api/cars`.

### Checkpoint 11 — Describe responses and validate filters

**Question 1: How is `CarInput` different from `Car`?**

**Model answer:** `CarInput` describes the editable content that the client submits. `Car` inherits those fields and adds the server-generated `id` to describe returned records. At checkpoint 11 it does not yet include `shortlisted`; that response field arrives at checkpoint 13.

**Question 2: Why does `category=Other` now produce 422 instead of an empty list?**

**Model answer:** The query parameter now uses the `Category` literal type instead of accepting any string. FastAPI rejects `Other` before the handler runs because it is not one of the four allowed values. Previously it was a valid string that simply matched no records.

### Checkpoint 12 — Introduce a related shortlist table

**Question 1: Why does a shortlist row need only a car ID?**

**Model answer:** The row records membership: this car is saved. The car's content already exists in `cars`, and a join retrieves it using the ID. Copying the content into the shortlist would create another copy to keep synchronized when the car changes.

**Question 2: What prevents duplicate entries, and what prevents references to missing cars?**

**Model answer:** The primary key on `shortlist.car_id` prevents two memberships for the same car. The foreign key to `cars(id)` prevents references to missing cars when foreign-key enforcement is enabled on the connection. `ON DELETE CASCADE` removes membership when its car is deleted.

### Checkpoint 13 — Expose shortlist state through the API

**Question 1: Why use a LEFT JOIN when listing all cars?**

**Model answer:** We need to keep cars that have no shortlist entry. A LEFT JOIN returns those cars too, with no matching membership value, so we can report `shortlisted: false`. An inner join would exclude unsaved cars from the main catalogue list.

**Question 2: If we submit `shortlisted: true` twice, what should the final state be?**

**Model answer:** The car remains saved with one membership row. This endpoint sets a state rather than toggling it. The first request inserts membership; the second succeeds without duplicating it because the insert uses `ON CONFLICT(car_id) DO NOTHING`.

### Checkpoint 14 — Automate backend checks

**Question 1: How do we know these tests won't change the demonstration database?**

**Model answer:** The database fixture uses `tmp_path` and patches `db.DATABASE_PATH` before the test client starts the application. Initialization and subsequent operations therefore use a temporary database. Pytest restores the patched attribute afterwards; the restart test deliberately reuses its temporary file within that one test.

**Question 2: Why test database constraints directly when we already test the HTTP endpoints?**

**Model answer:** API code can reject or handle an operation before SQL constraints are exercised. Direct SQL tests prove that the database itself rejects orphan references and duplicate membership, including writes made by scripts that bypass HTTP validation. Both layers need to behave correctly.
