from pydantic import BaseModel, EmailStr, Field

from app.models.enums import Role
from app.schemas.common import FromORM


class SignupForm(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)  # bcrypt ignores anything past 72 bytes
    role: Role = Role.CUSTOMER
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=255)
    restaurant_name: str | None = Field(default=None, max_length=150)  # owners only


class Credentials(BaseModel):
    email: EmailStr
    password: str


class AccountView(FromORM):
    id: int
    name: str
    email: EmailStr
    role: Role
    phone: str | None = None
    address: str | None = None


class SessionGrant(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AccountView


class Contact(FromORM):
    """The slice of an account other parties get to see (courier <-> customer, owner -> courier)."""

    id: int
    name: str
    phone: str | None = None
    address: str | None = None
