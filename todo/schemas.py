from ninja import Schema, ModelSchema

from .models import Task


class TaskCreateSchema(Schema):
    title = ''
    description = None
    status = "pending"
    due_date = None


class TaskOutSchema(ModelSchema):
    class Meta:
        model = Task
        model_fields = ('id', 'title', 'description', 'status', 'due_date', 'created_at')


class TaskFilterSchema(Schema):
    status = None
    sort_by_due = False
