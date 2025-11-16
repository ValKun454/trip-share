from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from decimal import Decimal

# User schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    email: str
    username: str | None = None
    is_verified: bool = Field(alias="isVerified")

class Token(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(alias="tokenType")

class TokenData(BaseModel):
    email: str | None = None

class Trip(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    name: str
    description: str | None = None
    created_at: datetime = Field(alias="createdAt")
    creator_id: int = Field(alias="creatorId")
    participants: list[int]

class TripCreate(BaseModel):
    name: str
    description: str
    participants: list[int]

class TripCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    name: str
    description: str | None = None
    created_at: datetime = Field(alias="createdAt")
    creator_id: int = Field(alias="creatorId")
    participants: list[int]


class Expense(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    is_scanned: bool = Field(alias="isScanned")
    name: str
    description: str
    created_at: datetime = Field(alias="createdAt")
    trip_id: int = Field(alias="tripId")
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal
    positions: list[int]

class ExpenseCreate(BaseModel):
    is_scanned: bool = Field(alias="isScanned")
    name: str
    description: str
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal

class ExpenseCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    is_scanned: bool = Field(alias="isScanned")
    name: str
    description: str
    created_at: datetime = Field(alias="createdAt")
    trip_id: int = Field(alias="tripId")
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal
    positions: list[int]