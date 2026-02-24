# Asynchronous Programming in FastAPI

FastAPI provides first-class support for **asynchronous programming**, enabling applications to handle thousands of concurrent connections efficiently without blocking execution. It leverages Python’s `async` / `await` syntax, the `asyncio` event loop, and the ASGI specification to deliver high-performance APIs.

Unlike traditional synchronous frameworks where each request may block a worker thread, FastAPI can pause tasks during I/O operations and allow other requests to execute. This makes it particularly powerful for I/O-bound applications such as APIs, microservices, and real-time systems.

---

## What Are Asynchronous Functions?

An asynchronous function is defined using `async def` instead of the traditional `def`:

```python
async def get_data():
    return {"message": "Hello, world"}
```

When an async function is called, it returns a **coroutine object** rather than immediately executing. A coroutine represents a task that can be suspended and resumed by the event loop.

Coroutines allow Python to:

- Pause execution at `await` points
- Perform other tasks while waiting
- Resume execution when the awaited operation completes

### I/O-Bound vs CPU-Bound Tasks

Async programming is most effective for **I/O-bound** tasks (waiting on external systems), not CPU-heavy computations.

Common operations that benefit from async execution:

- Database queries (PostgreSQL, MySQL, MongoDB)
- External API requests (HTTP calls)
- File system operations
- Network communication
- WebSocket communication
- Message queues (Kafka, Redis, RabbitMQ)

---

## The ASGI Standard

FastAPI is built on **ASGI (Asynchronous Server Gateway Interface)**, the asynchronous successor to WSGI.

- **WSGI** → Synchronous (Flask, traditional Django)
- **ASGI** → Asynchronous (FastAPI, Starlette)

ASGI enables:

- Long-lived connections
- WebSockets
- Background tasks
- Concurrent request handling

FastAPI runs on ASGI servers such as:

- `uvicorn`
- `hypercorn`
- `daphne`

Example:

```bash
uvicorn main:app --reload
```

---

## The Event Loop

The event loop is the core engine behind async execution.

It:

1. Schedules tasks  
2. Executes coroutines  
3. Pauses execution at `await`  
4. Switches to other tasks while waiting  
5. Resumes tasks when operations complete  

FastAPI typically uses:

- `asyncio` (Python’s built-in async framework)
- `uvloop` (a high-performance event loop implementation)

The event loop allows a single thread to handle many concurrent connections efficiently.

---

## How FastAPI Handles Sync vs Async Routes

FastAPI automatically detects whether a route handler is synchronous or asynchronous.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/async-example")
async def async_example():
    return {"status": "This is async"}

@app.get("/sync-example")
def sync_example():
    return {"status": "This is sync"}
```

### What Happens Internally?

- `async def` routes run directly inside the event loop.
- `def` routes run in a threadpool executor to avoid blocking the event loop.

This allows you to safely mix sync and async endpoints.

---

## The `await` Keyword

The `await` keyword pauses a coroutine until the awaited task completes.

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(2)
    return "Data loaded"
```

Without `await`, the coroutine would not yield control back to the event loop.

**Important:**  
You can only use `await` inside an `async def` function.

---

## Concurrency vs Parallelism

These concepts are often confused.

### Concurrency
- Multiple tasks making progress during overlapping time periods
- Achieved using async and event loops
- Best for I/O-bound workloads

### Parallelism
- Multiple tasks running simultaneously on multiple CPU cores
- Achieved using multiprocessing or multiple workers
- Best for CPU-bound workloads

FastAPI async provides concurrency, not CPU parallelism.

---

## Performance Characteristics

Async improves scalability because:

- Threads are not blocked during I/O
- Memory usage is lower than thread-per-request models
- Context switching is cheaper than OS thread switching

However:

- Async does not automatically make code faster
- Improper usage can reduce performance
- CPU-heavy work still requires multiple workers or multiprocessing

---

## Blocking vs Non-Blocking Code

Blocking code stops the event loop.

### ❌ Blocking Example

```python
import time
time.sleep(5)
```

### ✅ Non-Blocking Example

```python
import asyncio
await asyncio.sleep(5)
```

Other blocking tools to avoid in async routes:

- Synchronous database drivers
- `requests` library (use `httpx` instead)
- CPU-heavy loops

---

## Async Database & HTTP Libraries

To fully benefit from async, use async-compatible libraries:

- `asyncpg`
- `SQLAlchemy 2.0 async`
- `motor` (MongoDB)
- `databases`
- `httpx`

Example:

```python
import httpx

async def get_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()
```

---

## Background Tasks

FastAPI supports background execution without blocking responses.

```python
from fastapi import BackgroundTasks

@app.post("/send-email")
async def send_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_email)
    return {"message": "Email scheduled"}
```

This allows immediate responses while work continues in the background.

---

## When to Use Async vs Sync

### Use Async When:
- Waiting on databases
- Calling external APIs
- Handling file uploads
- Managing WebSockets
- Building high-concurrency APIs

### Use Sync When:
- Performing heavy computation
- Running CPU-intensive algorithms
- Image or video processing
- Machine learning inference

For CPU-heavy tasks, consider:

- Multiple workers (`uvicorn --workers`)
- Task queues (Celery)
- Multiprocessing

---

## Common Pitfalls

- Mixing blocking libraries inside async routes
- Forgetting `await`
- Assuming async improves CPU-bound performance
- Overusing async where it is unnecessary
- Not understanding that sync routes run in a threadpool

---

## Best Practices

- Use async libraries consistently
- Avoid blocking calls in async functions
- Profile before optimizing
- Use connection pooling for databases
- Load test your API
- Keep async functions small and focused

---

## Summary

Asynchronous programming enables FastAPI to:

- Efficiently handle many concurrent connections
- Improve scalability for I/O-heavy applications
- Reduce resource usage compared to thread-per-request models
- Maintain responsiveness under heavy workloads

By understanding coroutines, the event loop, ASGI, and proper async patterns, developers can build scalable, production-ready APIs suited for modern distributed systems.
