from pydantic import BaseModel, EmailStr

# User schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class Trip(BaseModel):
    id: str
    name: str
    dates: str
    participants: list[str]

class TripCreate(BaseModel):   # TODO: maybe add id as optional field later and delete second object TripCreateResponse
    name: str
    dates: str
    participants: list[str]

class TripCreateResponse(BaseModel):
    trip_id: int
    name: str
    dates: str
    participants: list[str]


class Expense(BaseModel):
    id: str
    trip_id: str
    title: str
    amount: float
    paid_by: str
    included: list[str]
    date: str

class ExpenseCreate(BaseModel):   #TODO: same as previous, combine two schemas by id optional
    trip_id: str
    title: str
    amount: float
    paid_by: str
    included: list[str]
    date: str

class ExpenseCreateResponse(BaseModel):
    id: int
    trip_id: int
    title: str
    amount: float
    paid_by: str
    included: list[str]
    date: str