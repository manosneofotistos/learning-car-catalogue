# Instructor guide: building the Car Catalogue API

## What we are building

We build a FastAPI backend for a curated catalogue of cars. A client can browse, search, create, edit, and delete cars, then save cars to one shared shortlist. SQLite stores the content and shortlist membership across server restarts. FastAPI's `/docs` page is our interactive client; this project has no browser frontend.

The teacher uses this car domain to demonstrate the same implementation that students will apply to places in `sibling-curated-guide`. Keep the supplied implementation, dependency versions, validation rules, and checkpoint order. The lesson progresses from Python lists to SQLite, then separates routing, describes API responses, adds a relationship, and automates checks.

The finished request flow is:

```text
HTTP request -> app/routes.py -> app/db.py -> data/catalogue.db
                    |               |
              app/models.py    app/schema.sql + app/seed.json at initialization

app/main.py creates the application, initializes the database, and registers routes.
```

### The data and API contract

| Field | Meaning | Validation |
| --- | --- | --- |
| `name` | Car name | String, 2–80 characters |
| `category` | Body category | `Hatchback`, `Sedan`, `SUV`, or `Coupe` |
| `manufacturer` | Manufacturer | String, 2–60 characters |
| `variant` | Version or trim | String, 3–120 characters |
| `description` | Curated description | String, 20–1000 characters |
| `tip` | Viewing or test-drive tip | String, 5–200 characters |
| `id` | Server-generated identity | Integer; returned, not submitted in the content body |
| `shortlisted` | Shared shortlist membership | Boolean; added to responses at checkpoint 13 |

`CarInput` strips surrounding string whitespace and rejects extra fields. POST and PUT accept the same six editable fields. PUT replaces all editable content. Shortlist membership has a separate request body and endpoint.

| Method | Path | Introduced | Success |
| --- | --- | --- | --- |
| GET | `/api/health` | 1 | 200, status object |
| GET | `/api/cars` | 2; filters at 3 | 200, array |
| GET | `/api/cars/{car_id}` | 2 | 200, car |
| POST | `/api/cars` | 4 | 201, created car |
| PUT | `/api/cars/{car_id}` | 5 | 200, updated car |
| DELETE | `/api/cars/{car_id}` | 5 | 204, empty body |
| GET | `/api/shortlist` | 13 | 200, array |
| PUT | `/api/cars/{car_id}/shortlist` | 13 | 200, car with resulting state |

Missing records produce 404. Invalid validated input produces 422. Text search uses the name, manufacturer, and description; category filtering requires an exact match.

## How to use the reference while teaching

This repository is the completed reference. Checkpoint labels and commented earlier implementations are teaching material, not Git branches or automatic switches. Read the reference on your private screen and build in a separate, initially empty working folder, such as `car-catalogue-live`. Keep the reference databases intact.

In [app/main.py](app/main.py), the first commented section contains checkpoints 1–5; the next contains the database-backed version for 8–9; the active section is the final assembly from 10. In [app/db.py](app/db.py), commented SELECT statements show the pre-shortlist queries. In [app/routes.py](app/routes.py), commented decorators show the pre-response-model routes.

When using an earlier commented implementation, remove one outer `# ` from its lines, preserving any actual inner comments. Select only the blocks for the current checkpoint. Do not uncomment the entire file: it contains successive versions of the same application and endpoints. Replace an earlier route when introducing its next version; keep only one active handler for each method/path pair.

Do not copy the finished `Car`, `ShortlistInput`, `CAR_SELECT`, or shortlist schema into earlier checkpoints. Their introduction is specified below. Some source comments still say “place” in the checkpoint 6 label; that exercise operates on cars.

### Checkpoint map

| Checkpoint | Outcome | File sequence |
| --- | --- | --- |
| 1 | A responding HTTP application | `requirements.txt` → `app/__init__.py` → `app/main.py` |
| 2 | Read an in-memory collection and one car | `app/main.py` |
| 3 | Search and category filters | `app/main.py` |
| 4 | Validate and create a car | `app/models.py` → `app/main.py` |
| 5 | Edit and delete in memory | `app/main.py` |
| 6 | Persist and read one car with SQLite scripts | `scripts/__init__.py` → create script → insert script → read script |
| 7 | Initialize and seed the application database | `app/schema.sql` → `app/seed.json` → `app/db.py` → inspection script |
| 8 | Read SQLite through HTTP | `app/db.py` → `app/main.py` |
| 9 | Write SQLite through HTTP | `app/db.py` → `app/main.py` |
| 10 | Separate routing from startup | `app/routes.py` → `app/main.py` |
| 11 | Validate filters and describe responses | `app/models.py` → `app/routes.py` |
| 12 | Model shortlist membership in SQL | `app/schema.sql` → `app/db.py` → relationship script |
| 13 | Expose shortlist state through HTTP | `app/db.py` → `app/models.py` → `app/routes.py` |
| 14 | Automate backend checks | `requirements.txt` → `tests/conftest.py` → `tests/test_api.py` |

Checkpoint 15 in the places project concerns its frontend and is outside this backend lesson.

## Terminal setup and conventions

All terminal examples below target Windows PowerShell 5.1 or PowerShell 7 on Windows, with Python 3.10 or newer. All later commands run from the live-build project root, where `app/` lives. Use two terminals in that same folder: terminal A runs the server; terminal B sends requests and runs scripts. Commands invoke the virtual environment directly, so activation is unnecessary.

From the parent projects directory, create a new folder that does not already contain a project:

**Windows PowerShell:**

```powershell
New-Item -ItemType Directory -Path car-catalogue-live
Set-Location car-catalogue-live
python -m venv .venv
New-Item -ItemType Directory -Path app
New-Item -ItemType File -Path app/__init__.py
```

Create files in your editor as each checkpoint calls for them. Copy the reference `.gitignore` into the live folder to exclude environments, caches, and local database files.

After checkpoint 1, start terminal A with:

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Use **Try it out** to submit requests and inspect status codes and bodies. `/` returns 404 because there is no frontend. Stop with Ctrl+C. Restart with the same command whenever a checkpoint requests it. Stop the server while making changes across multiple files, then restart once the files agree. Editing JSON or SQL alone may not trigger reload; explicitly restart after those changes.

In terminal B, define:

**Windows PowerShell:**

```powershell
$base = 'http://127.0.0.1:8000'
```

For each HTTP exercise, use the FastAPI `/docs` instructions first. Expand the named endpoint, click **Try it out**, fill in its parameters or JSON body, and click **Execute**. Read **Server response** for the actual status and body; the response descriptions below it are documentation, not execution results. Refresh `/docs` after changing routes or models.

The terminal examples are alternatives to the browser exercise. Choose either the browser or terminal sequence for each exercise; running both repeats writes and deletes. Use `curl.exe` explicitly for status checks to avoid PowerShell's `curl` alias. `Invoke-RestMethod` handles successful JSON requests in the examples.

Setup, package installation, starting/stopping the server, local SQLite scripts, and pytest require the terminal; `/docs` cannot run them. Browser actions do not set PowerShell variables. If switching to terminal exercises, define `$base` above and `$carBody` at checkpoint 4, then create the terminal exercise's own record to populate `$carId`. Repeat variables if you open a new terminal.

## Checkpoint 1 — Respond to an HTTP request

**Narration:** “Uvicorn receives the request. FastAPI matches its method and path to a Python function, then serializes the returned dictionary.”

1. Create `requirements.txt` with `fastapi==0.115.12` and `uvicorn==0.34.2`, using the reference comments. The test dependencies arrive at checkpoint 14.
2. Keep `app/__init__.py` empty.
3. Create `app/main.py`: import `FastAPI`, create `app = FastAPI(title="Car Catalogue API")`, and add the checkpoint 1 `GET /api/health` function.
4. Install the dependencies, then start the server using the terminal A command above.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**FastAPI `/docs` first:** execute **GET `/api/health`** without parameters. Expect HTTP 200 and `{"status":"ok"}`.

**Terminal alternative (terminal B):**

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
curl.exe -i "$base/api/health"
```

Expect HTTP 200 and `{"status":"ok"}`. Open `/docs` and point out the generated health endpoint. There is no database yet.

## Checkpoint 2 — Read cars from a Python list

**File sequence:** `app/main.py`, data first, handlers second.

1. Add the three-record `CARS` list from the first commented reference section. Preserve the supplied IDs, fields, and example content.
2. Add `GET /api/cars`, returning `CARS`.
3. Return to the imports and add `HTTPException`.
4. Add `GET /api/cars/{car_id}` with `car_id: int`. Loop through `CARS`, return a match, and raise 404 after the loop if none exists.

**Narration:** “The path chooses one record. A valid integer can still identify a record that does not exist.”

**FastAPI `/docs` first:** execute **GET `/api/cars`**. Then execute **GET `/api/cars/{car_id}`** with `1` and `999999` to see 200 and 404. The docs UI may block a non-integer `car_id` before sending; use the terminal's `not-an-integer` request to observe the server's 422.

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
curl.exe -i "$base/api/cars"
curl.exe -i "$base/api/cars/1"
curl.exe -i "$base/api/cars/999999"
curl.exe -i "$base/api/cars/not-an-integer"
```

Expect three cars; Toyota Corolla for ID 1; 404 with `This car does not exist.` for the missing ID; and 422 for the non-integer path parameter.

## Checkpoint 3 — Filter the collection

**File sequence:** replace only `list_cars()` in `app/main.py` with its checkpoint 3 implementation.

1. Add `q: str = ""` and `category: str | None = None` parameters.
2. Normalize search text using `strip().casefold()`.
3. Build a separate result list. Exclude nonmatching categories, combine the three searchable fields, and exclude nonmatching text.
4. Return the result list without changing `CARS`.

**Narration:** “Both filters must pass. An empty search imposes no text restriction.”

**FastAPI `/docs` first:** in **GET `/api/cars`**, execute these parameter combinations in order: `q=toyota` with category unset; `q=toyota` with `category=Coupe`; `q=spaceship` with category unset; and empty `q` with `category=Other`. Clear the previous values between cases. At this checkpoint, category is a free-text input.

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
curl.exe -i "$base/api/cars?q=toyota"
curl.exe -i "$base/api/cars?q=toyota&category=Coupe"
curl.exe -i "$base/api/cars?q=spaceship"
curl.exe -i "$base/api/cars?category=Other"
```

Expect two Toyotas; only Toyota GR86 with both filters; and an empty array for the last two requests. At this stage category is an unrestricted query string, so `Other` returns 200 with `[]`. Query category validation arrives at checkpoint 11.

## Checkpoint 4 — Validate input and create a car

**File sequence:** create `app/models.py` → return to `app/main.py`.

1. In `models.py`, add the `Literal` and Pydantic imports, `Category`, and `CarInput` exactly as in the reference. Stop before `class Car`; output models come later.
2. In `main.py`, import `CarInput` using `from .models import CarInput`.
3. Add the in-memory POST handler with `status_code=201`.
4. Calculate the next ID using the existing `max(..., default=0) + 1` expression, call `model_dump()`, add the ID, append to `CARS`, and return the new dictionary.

**Narration:** “The request supplies content. The server supplies identity. Validation happens before the handler changes the list.”

**FastAPI `/docs` first:** open **POST `/api/cars`**, click **Try it out**, and replace the example request body with:

```json
{
  "name": "Lesson Coupe",
  "category": "Coupe",
  "manufacturer": "Toyota",
  "variant": "Lesson Edition",
  "description": "A sample coupe used to demonstrate the catalogue API during the lesson.",
  "tip": "Check the driving position before a test drive."
}
```

Execute and expect 201. Note the returned `id`, then use it in **GET `/api/cars/{car_id}`**. Back in POST, try `"name": " "`, then an extra `"price": 100`, then `"category": "Other"`, restoring the valid body between cases. Each should return 422; GET the collection to confirm rejected requests did not add records.

**Terminal alternative:** define this reusable request body in terminal B:

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
$carBody = @{
    name = 'Lesson Coupe'
    category = 'Coupe'
    manufacturer = 'Toyota'
    variant = 'Lesson Edition'
    description = 'A sample coupe used to demonstrate the catalogue API during the lesson.'
    tip = 'Check the driving position before a test drive.'
}
$created = Invoke-RestMethod -Method Post -Uri "$base/api/cars" -ContentType 'application/json' -Body ($carBody | ConvertTo-Json)
$carId = $created.id
$created | ConvertTo-Json
curl.exe -i "$base/api/cars/$carId"
```

Expect the new car with an integer ID. In `/docs`, repeat POST to see HTTP 201 explicitly. Then submit a body with `name` set to one space: expect 422 and no new record. Demonstrate an extra field such as `price` and an invalid category: both also produce 422. Do not add these fields to the model.

The list exists only in this process. Restarting the server, including a reload after editing source, restores the original three cars.

## Checkpoint 5 — Replace and delete a car

**File sequence:** `app/main.py` imports → PUT handler → DELETE handler.

1. Add `Response` to the FastAPI imports.
2. Add the in-memory PUT handler. Use `enumerate()` to find the record's position, validate a complete `CarInput`, preserve the ID, and replace the dictionary at that position. Raise 404 if missing.
3. Add DELETE. Remove the matching item and immediately return `Response(status_code=204)`; otherwise raise 404.

**Narration:** “Editing preserves identity. Deletion succeeds with no response body. PUT requires every editable field.”

**FastAPI `/docs` first:** POST the checkpoint 4 JSON again and note its fresh ID. In **PUT `/api/cars/{car_id}`**, enter that ID and the complete body with `name` changed to `Updated Lesson Coupe`. Execute PUT and then GET that ID. Execute DELETE for it, then GET and DELETE again. Expect 200, 200, 204, 404, and 404 respectively. Before deleting, you can also submit PUT with only `{"name":"Updated Lesson Coupe"}` to show 422 for missing required fields.

**Terminal alternative:** source edits may have reloaded the server. Create a fresh record before testing:

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
$created = Invoke-RestMethod -Method Post -Uri "$base/api/cars" -ContentType 'application/json' -Body ($carBody | ConvertTo-Json)
$carId = $created.id
$carBody.name = 'Updated Lesson Coupe'
Invoke-RestMethod -Method Put -Uri "$base/api/cars/$carId" -ContentType 'application/json' -Body ($carBody | ConvertTo-Json)
curl.exe -i "$base/api/cars/$carId"
curl.exe -i -X DELETE "$base/api/cars/$carId"
curl.exe -i "$base/api/cars/$carId"
curl.exe -i -X DELETE "$base/api/cars/$carId"
```

Expect PUT and GET 200 with the same ID and updated name, DELETE 204 with no body, then GET and repeated DELETE 404. In `/docs`, try PUT with only a name: expect 422 because this is a complete replacement.

## Checkpoint 6 — Store and retrieve a car in SQLite

**File sequence:** `scripts/__init__.py` → `scripts/create_learning_database.py` → `scripts/insert_learning_car.py` → `scripts/read_learning_cars.py`.

1. Create `scripts/` and its empty `__init__.py`.
2. Build the create script from the reference: resolve the project root, create `data/`, connect to `data/learning.db`, create the simple `cars` table, commit, and close in `finally`.
3. Run it before building the insert script.
4. Build the insert script: require an existing database file, pass the six values separately from SQL through `?` placeholders, commit, print `lastrowid`, roll back on database errors, and close.
5. Run the insert script once.
6. Build the read script: use a new connection with `sqlite3.Row`, select ID/name/category in ID order, fetch rows, print them, and close.

**Terminal-only exercise:** `/docs` does not access `learning.db` or run these scripts.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m scripts.create_learning_database
.\.venv\Scripts\python.exe -m scripts.insert_learning_car
.\.venv\Scripts\python.exe -m scripts.read_learning_cars
.\.venv\Scripts\python.exe -m scripts.read_learning_cars
```

**Expected:** on a fresh database, insertion reports ID 1 and both reads report the same one Toyota Corolla. Each script is a separate process: the data outlives the process that inserted it. Running the insert script again creates another row; running create again does not erase rows.

**Narration:** “A connection is temporary; the database file persists. Commit makes the write durable, and placeholders keep values separate from SQL.”

The HTTP application still uses `CARS`. This exercise database is separate from the application database introduced next.

## Checkpoint 7 — Create and seed the application database

**File sequence:** `app/schema.sql` → `app/seed.json` → `app/db.py` → `scripts/inspect_catalogue_database.py`.

1. Create `schema.sql` with the reference `cars` table and its CHECK constraints, then the `app_metadata` table. Omit the `shortlist` table until checkpoint 12.
2. Create `seed.json` with the three reference cars and their six editable fields. SQLite supplies the IDs. This is JSON, so do not put Python comments in it.
3. Create `db.py`: imports, `APP_DIRECTORY`, `PROJECT_ROOT`, and `DATABASE_PATH` pointing to `data/catalogue.db`.
4. Add `connect()` with `sqlite3.Row`, the connection transaction context, and `finally: connection.close()`. Keep the reference `PRAGMA foreign_keys = ON`; explain its relationship effect at checkpoint 12.
5. Add `initialize()` exactly as supplied: execute the schema, start `BEGIN IMMEDIATE`, check the `seeded` metadata key, insert sample content only if the marker is absent, then insert the marker in the same transaction.
6. Add the `if __name__ == "__main__"` block at the bottom. No CRUD helpers or `CAR_SELECT` are needed yet.
7. Create the inspection script from the reference to print the ordered IDs/names and seed marker.

**Terminal-only exercise:** run initialization and inspect the seed marker locally. These operations have no `/docs` endpoint.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m app.db
.\.venv\Scripts\python.exe -m scripts.inspect_catalogue_database
.\.venv\Scripts\python.exe -m app.db
.\.venv\Scripts\python.exe -m scripts.inspect_catalogue_database
```

**Expected on a fresh live build:** both inspections show three cars, IDs 1–3, and `Seed marker: 1`. Reinitialization does not duplicate them. The completed reference's copied database may contain additional records; it is not the baseline for this fresh-build count.

**Narration:** “The schema creates missing tables. The marker records whether seeding already happened, even if every car is later deleted. The transaction keeps the seed decision and inserts together.”

Do not migrate `learning.db` into `catalogue.db`; they intentionally serve different teaching stages. Editing `seed.json` after seeding does not update existing rows. `CREATE TABLE IF NOT EXISTS` also does not modify an existing table definition.

## Checkpoint 8 — Read the database through HTTP

**File sequence:** `app/db.py` → `app/main.py`.

1. In `db.py`, add `list_cars()` and `get_car()` before the module's execution block.
2. Use the commented **plain SELECT** versions from the reference: select `id, name, category, manufacturer, variant, description, tip` directly from `cars`. There is no `CAR_SELECT` constant or shortlist join yet.
3. Keep the supplied list-query logic: fixed conditions, separate parameters, `instr(lower(...), lower(?))`, and `ORDER BY id`. For one record, return `None` if absent; otherwise return `dict(row)`.
4. Stop the server. In `main.py`, replace the in-memory stage with the checkpoint 8 section: import `asynccontextmanager` and `db`, define the lifespan calling `db.initialize()` before `yield`, and pass it to `FastAPI`.
5. Keep health and implement the two database-backed GET handlers. Translate a missing car into 404 in the route.
6. Remove the old `CARS` list and in-memory write handlers from the active application. This checkpoint temporarily exposes health and reads only; checkpoint 9 restores writes against SQLite. Do not leave GET reading SQLite while POST modifies an unrelated list.
7. Restart the server.

**FastAPI `/docs` first:** execute health, list cars with no filters, list with `q=toyota` and `category=Coupe`, and retrieve ID `999999`. Expect 200, 200, 200, and 404. Restart the server in terminal A and execute the unfiltered list again to show persistence.

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
curl.exe -i "$base/api/health"
curl.exe -i "$base/api/cars"
curl.exe -i "$base/api/cars?q=toyota&category=Coupe"
curl.exe -i "$base/api/cars/999999"
```

Expect 200, three seeded cars on a fresh build, Toyota GR86 for the combined filter, and 404. Stop and restart the server, then repeat GET: the same rows remain.

**Narration:** “Routes handle HTTP; database helpers handle SQL. Startup prepares persistence before the first request.” The earlier Python search used `casefold()`; the supplied SQLite search uses `lower()`, whose built-in case handling covers ASCII. Keep that existing implementation.

## Checkpoint 9 — Create, edit, and delete in SQLite

**File sequence:** `app/db.py` write helpers → `app/main.py` write handlers.

1. Add `create_car()` to `db.py`: parameterized INSERT, then read the new row using `cursor.lastrowid` in the same connection.
2. Add `update_car()`: parameterized UPDATE of the six fields, check `rowcount`, return `None` if missing, and select the updated row in the same transaction.
3. Add `delete_car()`: parameterized DELETE and a boolean result from `rowcount > 0`.
4. For create/update readbacks, use the reference's commented plain SELECT statements. Do not introduce shortlist joins yet.
5. Return to `main.py`: import `CarInput` and `Response` as needed and add the checkpoint 9 POST, PUT, and DELETE handlers. Pass `data.model_dump()` into database helpers; translate missing results into 404; preserve 201/204.
6. Restart the server.

**FastAPI `/docs` first:** POST the checkpoint 4 JSON and note the returned ID. Restart the server in terminal A, then GET that ID. PUT the complete body with `name` changed to `Persisted Lesson Coupe`, then GET it to confirm the update. Run the database inspection script below in PowerShell if you want to show the stored row directly. Finally DELETE that ID and GET it again: expect 204 then 404. `/docs` performs the HTTP operations; restarting and inspecting SQLite require the terminal.

**Terminal alternative:** create a new car:

**Windows PowerShell:**

```powershell
$created = Invoke-RestMethod -Method Post -Uri "$base/api/cars" -ContentType 'application/json' -Body ($carBody | ConvertTo-Json)
$carId = $created.id
$carId
```

Stop and restart terminal A, keeping terminal B open. Then:

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
curl.exe -i "$base/api/cars/$carId"
$carBody.name = 'Persisted Lesson Coupe'
Invoke-RestMethod -Method Put -Uri "$base/api/cars/$carId" -ContentType 'application/json' -Body ($carBody | ConvertTo-Json)
.\.venv\Scripts\python.exe -m scripts.inspect_catalogue_database
curl.exe -i -X DELETE "$base/api/cars/$carId"
curl.exe -i "$base/api/cars/$carId"
```

Expect the created record to survive restart, its updated name to appear in the database inspection, DELETE 204, and final GET 404. No fixed generated ID is assumed.

**Narration:** “The HTTP contract is familiar; persistence now supplies identity and stores the changes.”

## Checkpoint 10 — Separate routing from startup

**File sequence:** create `app/routes.py` → return to `app/main.py`.

1. Stop the server. Create `routes.py` with `APIRouter`, `HTTPException`, `Response`, `db`, and `CarInput` imports.
2. Define `router = APIRouter(prefix="/api", tags=["Catalogue"])`.
3. Move all six current handlers from `main.py` into `routes.py`. Change `@app` to `@router` and remove `/api` from decorator paths because the router supplies it.
4. Use the checkpoint 10 decorators without `response_model`. Keep `q: str = ""` and `category: str | None = None`. Do not yet import `Car`, `Query`, `Annotated`, or `ShortlistInput`.
5. Return to `main.py`. Keep lifespan and FastAPI construction, import `router`, and call `app.include_router(router)`. Remove the moved active handlers and their unused imports.
6. Restart the server and inspect `/docs`.

**FastAPI `/docs` first:** refresh the page and confirm six operations under `Catalogue`. Execute health, the car list with `q=toyota` and `category=Coupe`, and GET car ID `999999`. Then repeat checkpoint 9's POST, PUT, GET, and DELETE browser sequence to check the moved write routes.

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
curl.exe -i "$base/api/health"
curl.exe -i "$base/api/cars?q=toyota&category=Coupe"
curl.exe -i "$base/api/cars/999999"
```

Expect unchanged responses and six documented method/path operations under `Catalogue`. Repeat the checkpoint 9 create/update/delete commands to confirm the move preserved writes.

**Narration:** “`main.py` assembles the application. `routes.py` defines its HTTP interface. The public paths have not changed.”

## Checkpoint 11 — Describe responses and validate filters

**File sequence:** `app/models.py` → `app/routes.py`.

1. Add `class Car(CarInput)` with only `id: int`. Do not add `shortlisted` yet: database reads do not provide it until checkpoint 13.
2. In `routes.py`, import `Annotated`, `Query`, `Category`, and `Car`.
3. Add `response_model=list[Car]` to list and `response_model=Car` to get/create/update. Preserve POST 201. DELETE remains 204 with no response model.
4. Replace the list signature with the reference `Annotated` query definition: `q` has maximum length 100 and the supplied description; category becomes `Category | None`.
5. Restart and inspect both input and output schemas in `/docs`.

**FastAPI `/docs` first:** inspect the `CarInput` and `Car` schemas, then execute **GET `/api/cars`** with `q=toyota` and `category=Coupe`. To demonstrate query limits, try a 101-character `q`. The UI may reject oversized input locally, and its category dropdown may prevent choosing `Other`; use the terminal requests below to send these invalid values directly and observe the API's 422 responses.

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
curl.exe -i "$base/api/cars?category=Other"
$longQuery = 'x' * 101
curl.exe -i "$base/api/cars?q=$longQuery"
curl.exe -i "$base/api/cars?q=toyota&category=Coupe"
```

Expect 422 for the first two and 200 with Toyota GR86 for the third. Responses contain the six fields plus ID; they do not yet contain shortlist state.

**Narration:** “Input models describe accepted content. Response models describe returned content. Both appear in the generated API documentation.”

## Checkpoint 12 — Introduce a related shortlist table

**File sequence:** `app/schema.sql` → review `app/db.py` → `scripts/check_shortlist.py`.

1. Add the reference `shortlist` table to `schema.sql`. Its single column, `car_id`, is both the primary key and a foreign key to `cars(id)` with `ON DELETE CASCADE`.
2. Return to `db.py` and explain the existing `PRAGMA foreign_keys = ON` in `connect()`. SQLite needs this on every connection. Keep the pre-shortlist read queries for now.
3. Run initialization again to create the new table in the existing database. The seed marker still prevents duplicate cars.
4. Create `scripts/check_shortlist.py` exactly as supplied. Its `main()` creates its own temporary car, saves its ID, joins to the car, checks duplicate rejection, deletes the parent, verifies cascade cleanup, and checks orphan rejection. Preserve its `finally` cleanup.

**Terminal-only exercise:** the shortlist HTTP endpoints arrive at checkpoint 13. `/docs` cannot execute the raw SQL constraint checks.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m app.db
.\.venv\Scripts\python.exe -m scripts.check_shortlist
```

Expect all five relationship messages followed by `All shortlist relationship checks passed.` The script removes its own example. Catching the expected integrity errors is part of this successful exercise.

**Narration:** “Membership stores an identity, not another copy of the car. The primary key prevents duplicate membership; the foreign key prevents orphan membership; deleting the parent removes its membership.”

The HTTP shortlist endpoints are not present yet. This checkpoint demonstrates the relationship directly in SQLite.

## Checkpoint 13 — Expose shortlist state through the API

**File sequence:** `app/db.py` → `app/models.py` → `app/routes.py`.

1. Stop the server. In `db.py`, add the supplied `CAR_SELECT` constant above the helpers. Its LEFT JOIN keeps every car and calculates membership with `(s.car_id IS NOT NULL) AS shortlisted`.
2. Return to **all four** existing read locations: list, get, create readback, and update readback. Replace their plain SELECTs with the reference `CAR_SELECT` versions. Preserve filtering and ordering. This ensures every car-returning endpoint supplies the new field.
3. Add `list_shortlist()` and `set_shortlisted()`. Preserve `BEGIN IMMEDIATE`, existence checking, `ON CONFLICT(car_id) DO NOTHING`, removal, and reading the result before commit.
4. In `models.py`, add `shortlisted: bool` to `Car`. Add `ShortlistInput` with `extra="forbid"`, `strict=True`, and its boolean field.
5. In `routes.py`, import `ShortlistInput` and add GET `/shortlist` and PUT `/cars/{car_id}/shortlist` with their response models and 404 handling.
6. Restart. There are now eight API operations. SQLite produces integer membership values; the `Car` response model renders JSON booleans. The shortlist request model separately requires actual JSON booleans.

**FastAPI `/docs` first:** POST the checkpoint 4 body and note the ID; its response has `shortlisted: false`. Open **PUT `/api/cars/{car_id}/shortlist`**, enter that ID, and submit `{"shortlisted":true}` twice. Both responses show `true`. Execute **GET `/api/shortlist`**: this ID appears once. Restart the server in terminal A and GET the shortlist again to confirm persistence.

**Terminal alternative:** create a dedicated example and save it twice:

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
$created = Invoke-RestMethod -Method Post -Uri "$base/api/cars" -ContentType 'application/json' -Body ($carBody | ConvertTo-Json)
$carId = $created.id
$saveBody = @{ shortlisted = $true } | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "$base/api/cars/$carId/shortlist" -ContentType 'application/json' -Body $saveBody
Invoke-RestMethod -Method Put -Uri "$base/api/cars/$carId/shortlist" -ContentType 'application/json' -Body $saveBody
curl.exe -i "$base/api/shortlist"
```

Expect the created car initially to have `shortlisted: false`, both saves to return `true`, and one membership for this ID. Restart the server and GET the shortlist again: membership persists.

**FastAPI `/docs` first:** for the same ID, execute the shortlist PUT twice with `{"shortlisted":false}`. GET the car to show it still exists. Save it again with `true`, DELETE the car, then GET the shortlist to show the membership disappeared. Before deleting, submit `{"shortlisted":"true"}` to demonstrate 422. With a valid boolean body and missing ID `999999`, expect 404.

**Terminal alternative:** remove membership twice, then save again and delete the car:

**Windows PowerShell (using `curl.exe` for status checks):**

```powershell
$removeBody = @{ shortlisted = $false } | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "$base/api/cars/$carId/shortlist" -ContentType 'application/json' -Body $removeBody
Invoke-RestMethod -Method Put -Uri "$base/api/cars/$carId/shortlist" -ContentType 'application/json' -Body $removeBody
curl.exe -i "$base/api/cars/$carId"
Invoke-RestMethod -Method Put -Uri "$base/api/cars/$carId/shortlist" -ContentType 'application/json' -Body $saveBody
curl.exe -i -X DELETE "$base/api/cars/$carId"
curl.exe -i "$base/api/shortlist"
```

Expect repeated removal to succeed with `false`; the car still exists after unsaving. Deleting the saved car removes its membership. In `/docs`, sending `{"shortlisted":"true"}` produces 422; saving a missing ID with a valid boolean produces 404.

**Narration:** “This endpoint sets the requested state. Repeating a save does not toggle it or create duplicates. The shortlist is shared by every client; there are no user accounts in this implementation.”

## Checkpoint 14 — Automate backend checks

**File sequence:** `requirements.txt` → `tests/conftest.py` → `tests/test_api.py`, adding and running one test at a time.

**Terminal-only automation:** the HTTP behaviors can be demonstrated through `/docs` as above, but installing packages, running pytest, creating isolated test databases, and asserting raw SQL failures require PowerShell.

1. Append `pytest==8.3.5` and `httpx==0.28.1` with the reference comments, then install again:

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

2. Create `tests/conftest.py`. First write `database(tmp_path, monkeypatch)` to redirect `db.DATABASE_PATH` to a temporary file; then `client(database)` using `with TestClient(app)` so lifespan runs; then `example_car()` returning fresh valid content.
3. Create `tests/test_api.py` with the reference imports and `test_list_filters_and_missing_car`. Run it:

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py::test_list_filters_and_missing_car
```

4. Return to `test_api.py` and add `test_invalid_input_does_not_create_a_car`. It checks rejected input, query validation, and strict shortlist booleans without unintended changes.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py::test_invalid_input_does_not_create_a_car
```

5. Add `test_car_lifecycle_and_shortlist` to check creation, retrieval, replacement, repeated save/removal, deletion, cascade cleanup, and missing-record responses.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py::test_car_lifecycle_and_shortlist
```

6. Add `test_restart_preserves_data_without_reseeding`. Follow its explicit `TestClient` contexts: the same temporary database survives application restarts, and deleting all cars does not trigger reseeding.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py::test_restart_preserves_data_without_reseeding
```

7. Add `test_database_rejects_orphans_and_duplicate_membership`. It deliberately writes SQL directly to verify database constraints independently of HTTP validation.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py::test_database_rejects_orphans_and_duplicate_membership
.\.venv\Scripts\python.exe -m pytest -q
```

**Expected:** five passing tests. Uvicorn need not be running: `TestClient` runs the app in process. Tests use temporary databases and leave the live catalogue untouched. Depending on installed transitive dependencies, the pinned stack may emit an AnyIO/Starlette deprecation warning; distinguish that warning from a failing test rather than changing lesson dependencies.

**Narration:** “We now repeat the behaviors we demonstrated manually, with isolated data and assertions that make failures visible.”

## End-of-lesson verification and file map

**FastAPI `/docs` first:** with Uvicorn running, show all eight operations. Repeat checkpoint 13's browser sequence to demonstrate membership and deletion, and checkpoint 9's restart check to demonstrate persistence. Use the terminal for server restarts.

**Terminal-only verification:** from the completed live-build root, initialize and inspect the database, run the direct relationship checks, and run pytest:

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m app.db
.\.venv\Scripts\python.exe -m scripts.inspect_catalogue_database
.\.venv\Scripts\python.exe -m scripts.check_shortlist
.\.venv\Scripts\python.exe -m pytest -q
```

Then start Uvicorn and use `/docs` to show all eight API operations. Health responds, filters work, edits survive restart, saving twice creates one membership, and deleting a saved car removes that membership.

| Reference file | Responsibility |
| --- | --- |
| [app/main.py](app/main.py) | Application assembly and lifespan; commented earlier HTTP stages |
| [app/models.py](app/models.py) | Input and response contracts |
| [app/routes.py](app/routes.py) | Methods, paths, HTTP status codes, validation wiring |
| [app/db.py](app/db.py) | Connections, transactions, initialization, SQL operations |
| [app/schema.sql](app/schema.sql) | Tables and database constraints |
| [app/seed.json](app/seed.json) | Initial catalogue content |
| [scripts/create_learning_database.py](scripts/create_learning_database.py) | First SQLite table exercise |
| [scripts/insert_learning_car.py](scripts/insert_learning_car.py) | First durable insert |
| [scripts/read_learning_cars.py](scripts/read_learning_cars.py) | Read using a new connection |
| [scripts/inspect_catalogue_database.py](scripts/inspect_catalogue_database.py) | Inspect application rows and seed marker |
| [scripts/check_shortlist.py](scripts/check_shortlist.py) | Exercise relationship constraints and cascade |
| [tests/conftest.py](tests/conftest.py) | Isolated database and client fixtures |
| [tests/test_api.py](tests/test_api.py) | Five backend behavior tests |

### If a checkpoint does not behave as expected

| Symptom | Check |
| --- | --- |
| `No module named app` or a relative-import error | Run from the project root using `-m app.db`, `-m scripts...`, or `-m uvicorn app.main:app`; do not run `app/main.py` directly. |
| A changed handler seems ignored | Remove its earlier active decorator/function. There must be one active handler per method/path. |
| A newly created in-memory car disappears | Before checkpoint 9, reload/restart resets the Python list. Create a fresh example after source edits. |
| Reads do not show a script's inserted car | `learning.db` is the checkpoint 6 exercise; HTTP reads `catalogue.db` from checkpoint 8. |
| `no such table: shortlist` | Apply checkpoint 12 schema and run initialization before checkpoint 13 joins. |
| Response validation fails for `shortlisted` | Add the field only at checkpoint 13 and update list/get/create/update read queries together. |
| Seed changes do not appear | The database's seed marker prevents reinsertion. Use a fresh live-build folder for a fresh lesson; existing content is intentionally preserved. |
| `/api/api/cars` appears | At checkpoint 10, remove `/api` from decorators because the router already has that prefix. |
| Port 8000 is already in use | Stop the other lesson/reference server, then start the intended project from its root. |

When students apply the lesson to places, the model, SQL, examples, and entity paths receive the corresponding domain names. The control flow, persistence approach, relationship behavior, and testing sequence stay the same.
