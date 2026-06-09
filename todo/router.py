from ninja import Router, Query
from django.shortcuts import get_object_or_404
from typing import List

from .models import Task
from .schemas import TaskCreateSchema, TaskOutSchema, TaskFilterSchema
from .auth import jwt_auth

router = Router(tags=["Tasks"])

@router.get("/", response=List[TaskOutSchema], auth=jwt_auth)
def list_tasks(request, filters: TaskFilterSchema = Query(...)):
    queryset = Task.objects.filter(user=request.auth)
    if filters.status in ['pending', 'completed']:
        queryset = queryset.filter(status=filters.status)
    if filters.sort_by_due == "desc":
        queryset = queryset.order_by('-due_date')
    else:
        queryset = queryset.order_by('due_date')
    return queryset

@router.post("/", response=TaskOutSchema, auth=jwt_auth)
def create_task(request, payload: TaskCreateSchema):
    return Task.objects.create(user=request.auth, **payload.dict())

@router.get("/{task_id}", response=TaskOutSchema, auth=jwt_auth)
def get_task(request, task_id: int):
    return get_object_or_404(Task, id=task_id, user=request.auth)

@router.put("/{task_id}", response=TaskOutSchema, auth=jwt_auth)
def update_task(request, task_id: int, payload: TaskCreateSchema):
    task = get_object_or_404(Task, id=task_id, user=request.auth)
    for attr, value in payload.dict().items():
        setattr(task, attr, value)
    task.save()
    return task

@router.delete("/{task_id}", auth=jwt_auth)
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id, user=request.auth)
    task.delete()
    return {"success": True, "message": f"Завдання №{task_id} успішно видалено"}
