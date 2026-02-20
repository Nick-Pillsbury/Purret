from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import asyncio
import uuid

app = FastAPI(title="Task Manager API")

# Data Models
class Task(BaseModel):
    id: str
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=5)
    completed: bool = False


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=5)

# In-memory "database"
tasks: List[Task] = []


# Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Task Manager API"}


# CREATE TASK (Async example)
@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    await asyncio.sleep(0.5)  # Simulate async DB call
    
    new_task = Task(
        id=str(uuid.uuid4()),
        title=task.title,
        description=task.description,
        completed=False
    )
    
    tasks.append(new_task)
    return new_task


# GET ALL TASKS
@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks


# GET SINGLE TASK
@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


# UPDATE TASK (Sync example)
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, updated: TaskCreate):
    for task in tasks:
        if task.id == task_id:
            task.title = updated.title
            task.description = updated.description
            return task
    raise HTTPException(status_code=404, detail="Task not found")


# DELETE TASK
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")