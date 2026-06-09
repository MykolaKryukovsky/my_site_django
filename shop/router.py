from ninja import Router
from django.shortcuts import get_object_or_404
from django.db import transaction
from ninja.errors import HttpError
from typing import List

from .models import Product, CartItem, Order, OrderItem
from .schemas import (
    ProductCreateSchema, ProductOutSchema,
    CartItemInSchema, CartItemOutSchema,
    OrderOutSchema, OrderStatusUpdateSchema
)
from todo.auth import jwt_auth


router = Router(tags=["Shop"])


@router.get("/products", response=List[ProductOutSchema])
def list_products(request):
    """Отримання списку всіх товарів."""
    return Product.objects.all()


@router.get("/products/{product_id}", response=ProductOutSchema)
def get_product(request, product_id: int):
    """Перегляд конкретного товару за ID."""
    return get_object_or_404(Product, id=product_id)


@router.post("/products", response=ProductOutSchema, auth=jwt_auth)
def create_product(request, payload: ProductCreateSchema):
    """Створення нового товару."""
    return Product.objects.create(**payload.dict())


@router.put("/products/{product_id}", response=ProductOutSchema, auth=jwt_auth)
def update_product(request, product_id: int, payload: ProductCreateSchema):
    """Оновлення товару."""
    product = get_object_or_404(Product, id=product_id)
    for attr, value in payload.dict().items():
        setattr(product, attr, value)
    product.save()
    return product


@router.delete("/products/{product_id}", auth=jwt_auth)
def delete_product(request, product_id: int):
    """Видалення товару."""
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"success": True, "message": "Товар успішно видалено"}


@router.get("/cart", response=List[CartItemOutSchema], auth=jwt_auth)
def view_cart(request):
    """Перегляд кошика поточного користувача."""
    return CartItem.objects.filter(user=request.auth).select_related('product')


@router.post("/cart", auth=jwt_auth)
def add_to_cart(request, payload: CartItemInSchema):
    """Додавання товару до кошика / збільшення кількості."""
    product = get_object_or_404(Product, id=payload.product_id)

    if product.stock < payload.quantity:
        raise HttpError(400, f"Недостатньо товару на складі. Доступно: {product.stock}")

    cart_item, created = CartItem.objects.get_or_create(
        user=request.auth,
        product=product,
        defaults={'quantity': payload.quantity}
    )
    if not created:
        cart_item.quantity += payload.quantity
        cart_item.save()

    return {"success": True, "message": "Товар додано до кошика"}


@router.delete("/cart/{product_id}", auth=jwt_auth)
def remove_from_cart(request, product_id: int):
    """Видалення товару з кошика."""
    cart_item = get_object_or_404(CartItem, user=request.auth, product_id=product_id)
    cart_item.delete()
    return {"success": True, "message": "Товар видалено з кошика"}


@router.post("/orders", response=OrderOutSchema, auth=jwt_auth)
def checkout(request):
    """Оформлення замовлення з товарів у кошику."""
    cart_items = CartItem.objects.filter(user=request.auth).select_related('product')

    if not cart_items.exists():
        raise HttpError(400, "Кошик порожній.")

    with transaction.atomic():
        order = Order.objects.create(user=request.auth, total_price=0)
        total = 0

        for item in cart_items:
            if item.product.stock < item.quantity:
                raise HttpError(400, f"Товар '{item.product.title}' закінчився на складі.")

            item.product.stock -= item.quantity
            item.product.save()

            total += item.product.price * item.quantity

            OrderItem.objects.create(
                order=order,
                product=item.product,
                title=item.product.title,
                price=item.product.price,
                quantity=item.quantity
            )

        order.total_price = total
        order.save()
        cart_items.delete()  # Очищаем корзину

    return order


@router.get("/orders", response=List[OrderOutSchema], auth=jwt_auth)
def list_orders(request):
    """Перегляд історії замовлень користувача."""
    return Order.objects.filter(user=request.auth).prefetch_related('items')


@router.patch("/orders/{order_id}/status", response=OrderOutSchema, auth=jwt_auth)
def update_order_status(request, order_id: int, payload: OrderStatusUpdateSchema):
    """Зміна статусу замовлення (processing, shipped, delivered, cancelled)."""
    if payload.status not in ['processing', 'shipped', 'delivered', 'cancelled']:
        raise HttpError(400, "Недійсний статус замовлення.")

    order = get_object_or_404(Order, id=order_id)
    order.status = payload.status
    order.save()
    return order
