# Asynchronous Programming in FastAPI

FastAPI provides built-in support for **asynchronous programming**,
allowing applications to handle many requests efficiently without
blocking execution. This is achieved using Python's `async` and `await`
keywords and an event-driven execution model.

By using asynchronous functions correctly, developers can build
high-performance, scalable APIs that remain responsive even under heavy
workloads.

------------------------------------------------------------------------

## What Are Asynchronous Functions?

An asynchronous function is defined using the `async def` syntax instead
of the traditional `def` keyword:

``` python
async def get_data():
    return {"message": "Hello, world"}
```

When an async function is called, it returns a **coroutine object**. A
coroutine represents a task that can be paused and resumed during
execution.

Common operations that benefit from async execution include:

-   Database queries\
-   External API requests\
-   File reading and writing\
-   Network communication\
-   WebSocket communication

------------------------------------------------------------------------

## The Event Loop

The event loop schedules tasks, runs coroutines, pauses and resumes
execution, and manages I/O operations.

FastAPI uses an event loop (usually provided by `uvicorn` and `asyncio`)
to manage async functions.

------------------------------------------------------------------------

## How FastAPI Uses Asynchronous Functions

FastAPI automatically detects whether a route handler is synchronous or
asynchronous.

``` python
from fastapi import FastAPI

app = FastAPI()

@app.get("/async-example")
async def async_example():
    return {"status": "This is async"}

@app.get("/sync-example")
def sync_example():
    return {"status": "This is sync"}
```

------------------------------------------------------------------------

## The `await` Keyword

``` python
import asyncio

async def fetch_data():
    await asyncio.sleep(2)
    return "Data loaded"
```

------------------------------------------------------------------------

## Benefits

-   High performance under load\
-   Non-blocking operations\
-   Efficient resource usage\
-   Better responsiveness

------------------------------------------------------------------------

## When to Use Async vs Sync

### Async

-   APIs
-   Databases
-   Network I/O

### Sync

-   Heavy computation
-   Image processing

------------------------------------------------------------------------

## Blocking vs Non-Blocking

Bad:

``` python
time.sleep(5)
```

Good:

``` python
await asyncio.sleep(5)
```

------------------------------------------------------------------------

## Best Practices

-   Avoid blocking calls
-   Use async libraries
-   Profile performance

------------------------------------------------------------------------

## Summary

Asynchronous programming enables FastAPI to scale efficiently and remain
responsive under heavy workloads.
