import time
from fastapi import FastAPI, HTTPException, Request, status, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from models import AnimalCreate, AnimalUpdate, AnimalOut, Status
from storage import get_storage

app = FastAPI(
    title="Lab 1: Приют для животных",
    description="In-memory CRUD for animals and adoption requests",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_detail = exc.errors()[0]
    field_name = error_detail.get("loc")[-1]
    error_msg = error_detail.get("msg")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": error_msg, "field": field_name},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Блок **: Логирование (Middleware) ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        process_time = (time.perf_counter() - start_time) * 1000
        storage.add_log(request.method, request.url.path, 500, process_time)
        raise
    process_time = (time.perf_counter() - start_time) * 1000
    status_code = response.status_code

    storage.add_log(request.method, request.url.path, status_code, process_time)
    return response


# --- Инициализация хранилища ---
storage = get_storage()


# --- Блок здоровья ---
@app.get("/health", status_code=200)
async def health():
    return {"status": "ok"}


# --- CRUD Endpoints ---
RESOURCE_PATH = "/api/animals"


@app.get(f"{RESOURCE_PATH}", response_model=list[AnimalOut])
async def list_animals(limit: int = 10, offset: int = 0, status: Status | None = None, species: str | None = None):
    items = list(storage.values())
    if status:
        items = [item for item in items if item.status == status]
    if species:
        items = [item for item in items if item.species.lower() == species.lower()]
    total = len(items)
    paginated = items[offset: offset + limit]

    return paginated


@app.get(f"{RESOURCE_PATH}/{{animal_id}}", response_model=AnimalOut)
async def get_animal(animal_id: int):
    item = storage.get(animal_id)
    if not item:
        raise HTTPException(status_code=404, detail="Animal not found")
    return item


@app.post(f"{RESOURCE_PATH}", response_model=AnimalOut, status_code=status.HTTP_201_CREATED)
async def create_animal(payload: AnimalCreate):
    animal_id = storage.get_next_id()
    item = AnimalOut(id=animal_id, **payload.model_dump())
    storage.save(animal_id, item)
    return item


@app.put(f"{RESOURCE_PATH}/{{animal_id}}", response_model=AnimalOut)
async def update_animal(animal_id: int, payload: AnimalCreate):
    existing = storage.get(animal_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    item = AnimalOut(id=animal_id, **payload.model_dump())
    storage.save(animal_id, item)
    return item


@app.patch(f"{RESOURCE_PATH}/{{animal_id}}", response_model=AnimalOut)
async def partial_update_animal(animal_id: int, payload: AnimalUpdate):
    existing = storage.get(animal_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "status" in update_data and isinstance(update_data["status"], str):
        update_data["status"] = Status(update_data["status"])
    updated_item = existing.copy(update=update_data)
    storage.save(animal_id, updated_item)
    return updated_item


@app.delete(f"{RESOURCE_PATH}/{{animal_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(animal_id: int):
    existing = storage.get(animal_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    storage.delete(animal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/logs", response_model=dict)
async def get_logs(limit: int = 50, offset: int = 0):
    global storage
    logs_data = storage.get_logs(limit=limit, offset=offset)
    items_as_dict = [
        {
            "timestamp": log.timestamp,
            "method": log.method,
            "path": log.path,
            "status": log.status,
            "duration_ms": log.duration_ms
        }
        for log in logs_data["items"]
    ]
    return {
        "total": logs_data["total"],
        "limit": logs_data["limit"],
        "offset": logs_data["offset"],
        "items": items_as_dict
    }

