from ninja import NinjaAPI
from todo.router import router as todo_router
from shop.router import router as shop_router


api = NinjaAPI(
    title="Universal Project API",
    version="1.0.0",
    description="Єдина платформа: Диспетчер задач + Інтернет-магазин"
)


api.add_router("/tasks", todo_router)
api.add_router("/shop", shop_router)
