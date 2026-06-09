from ninja import Schema, ModelSchema
from typing import List, Optional
from decimal import Decimal
from .models import Product, Order, OrderItem


class ProductCreateSchema(Schema):
    title: str
    description: Optional[str] = None
    price: Decimal
    stock: int = 0


class ProductOutSchema(ModelSchema):
    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'price', 'stock')


class CartItemInSchema(Schema):
    product_id: int
    quantity = 1


class CartItemOutSchema(Schema):
    id: int
    product: ProductOutSchema
    quantity: int


class OrderItemOutSchema(ModelSchema):
    class Meta:
        model = OrderItem
        fields = ('id', 'title', 'price', 'quantity')


class OrderOutSchema(ModelSchema):
    items: List[OrderItemOutSchema]
    class Meta:
        model = Order
        fields = ('id', 'status', 'total_price', 'created_at', 'items')


class OrderStatusUpdateSchema(Schema):
    status: str
