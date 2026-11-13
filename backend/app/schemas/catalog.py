from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import FromORM



class RestaurantCard(FromORM):
    id: int
    name: str
    description: str | None = None
    cuisine: str | None = None
    address: str | None = None
    image_url: str | None = None
    avg_rating: float | None = None
    review_count: int = 0


class RestaurantPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    cuisine: str | None = None
    address: str | None = None
    image_url: str | None = None


class DishForm(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str | None = Field(default=None, max_length=80)
    image_url: str | None = Field(default=None, max_length=500)
    is_available: bool = True


class DishPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    category: str | None = None
    image_url: str | None = None
    is_available: bool | None = None


class AvailabilityToggle(BaseModel):
    is_available: bool


class DishView(FromORM):
    id: int
    restaurant_id: int
    name: str
    description: str | None = None
    price: Decimal
    category: str | None = None
    image_url: str | None = None
    is_available: bool


class ReviewView(FromORM):
    id: int
    order_id: int
    rating: int
    comment: str | None = None
    created_at: datetime
    customer_name: str | None = None
