from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

ItemT = TypeVar("ItemT")


class FromORM(BaseModel):
    """Base for response models that are built straight from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class Paginated(BaseModel, Generic[ItemT]):
    items: list[ItemT]
    total: int
    page: int
    page_size: int
    pages: int
