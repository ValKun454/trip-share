from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, date
from decimal import Decimal

# User schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=40)
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    email: str
    username: str | None = Field(default=None, max_length=40)
    is_verified: bool = Field(alias="isVerified")

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=40)
    password: str | None = Field(default=None, min_length=8)

class Token(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(alias="tokenType")

class TokenData(BaseModel):
    email: str | None = None

class Trip(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(alias="createdAt")
    creator_id: int = Field(alias="creatorId")
    participants: list[int]

class TripCreate(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    participants: list[int]

class TripCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(alias="createdAt")
    creator_id: int = Field(alias="creatorId")
    participants: list[int]

class TripUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    beginning_date: date | None = Field(default=None, alias="beginningDate")
    end_date: date | None = Field(default=None, alias="endDate")
    participants: list[int] | None = None


class Expense(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    is_scanned: bool = Field(alias="isScanned")
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    beginning_date: date = Field(alias="beginningDate")
    end_date: date = Field(alias="endDate")
    created_at: datetime = Field(alias="createdAt")
    trip_id: int = Field(alias="tripId")
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal
    positions: list[int]

class ExpenseCreate(BaseModel):
    is_scanned: bool = Field(alias="isScanned")
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    beginning_date: date = Field(alias="beginningDate")
    end_date: date = Field(alias="endDate")
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal

class ExpenseCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    is_scanned: bool = Field(alias="isScanned")
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    beginning_date: date = Field(alias="beginningDate")
    end_date: date = Field(alias="endDate")
    created_at: datetime = Field(alias="createdAt")
    trip_id: int = Field(alias="tripId")
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal
    positions: list[int]

class ExpenseUpdate(BaseModel):
    is_scanned: bool | None = Field(default=None, alias="isScanned")
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    beginning_date: date | None = Field(default=None, alias="beginningDate")
    end_date: date | None = Field(default=None, alias="endDate")
    payer_id: int | None = Field(default=None, alias="payerId")
    is_even_division: bool | None = Field(default=None, alias="isEvenDivision")
    total_cost: Decimal | None = None

class Position(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    expense_id: int = Field(alias="expenseId")
    participant_id: int = Field(alias="participantId")

class PositionCreate(BaseModel):
    participant_id: int = Field(alias="participantId")

class PositionUpdate(BaseModel):
    participant_id: int = Field(alias="participantId")

class FriendResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    user_id_1: int = Field(alias="userId1")
    user_id_2: int = Field(alias="userId2")
    friend_username: str | None = Field(default=None, alias="friendUsername")

class FriendCreate(BaseModel):
    friend_id: int = Field(alias="friendId")

class FriendUser(BaseModel):
    """Schema for returning user info in friendlist"""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    username: str