from pydantic import BaseModel, EmailStr, Field, ConfigDict

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
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    dates: str
    participants: list[str]

class TripCreate(BaseModel):
    name: str
    dates: str
    participants: list[str]

class TripCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    trip_id: int = Field(alias="tripId")
    name: str
    dates: str
    participants: list[str]


class Expense(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    trip_id: str = Field(alias="tripId")
    title: str
    amount: float
    paid_by: str = Field(alias="paidBy")
    included: list[str]
    date: str

class ExpenseCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    trip_id: str = Field(alias="tripId")
    title: str
    amount: float
    paid_by: str = Field(alias="paidBy")
    included: list[str]
    date: str

class ExpenseCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    trip_id: int = Field(alias="tripId")
    title: str
    amount: float
    paid_by: str = Field(alias="paidBy")
    included: list[str]
    date: str