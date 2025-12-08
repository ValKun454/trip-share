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
    beginning_date: date | None = Field(default=None, alias="beginningDate")
    end_date: date | None = Field(default=None, alias="endDate")
    created_at: datetime = Field(alias="createdAt")
    creator_id: int = Field(alias="creatorId")
    participants: list[int]

class TripCreate(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    beginning_date: date | None = Field(default=None, alias="beginningDate")
    end_date: date | None = Field(default=None, alias="endDate")

class TripCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
    beginning_date: date | None = Field(default=None, alias="beginningDate")
    end_date: date | None = Field(default=None, alias="endDate")
    created_at: datetime = Field(alias="createdAt")
    creator_id: int = Field(alias="creatorId")
    participants: list[int]

class TripUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    beginning_date: date | None = Field(default=None, alias="beginningDate")
    end_date: date | None = Field(default=None, alias="endDate")

# Expense schemas

# New schema for participant share in expense responses
class ParticipantShareResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str
    is_paying: bool = Field(alias="isPaying")
    amount: str  # Using string for Decimal in JSON

# Updated Expense schema with participant shares
class Expense(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    is_scanned: bool = Field(alias="isScanned")
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    created_at: datetime = Field(alias="createdAt")
    trip_id: int = Field(alias="tripId")
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal = Field(alias="totalCost")
    participant_shares: list[ParticipantShareResponse] = Field(alias="participantShares")

class ExpenseCreate(BaseModel):
    is_scanned: bool = Field(alias="isScanned")
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal = Field(alias="totalCost")

class ExpenseCreateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    is_scanned: bool = Field(alias="isScanned")
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    created_at: datetime = Field(alias="createdAt")
    trip_id: int = Field(alias="tripId")
    payer_id: int = Field(alias="payerId")
    is_even_division: bool = Field(alias="isEvenDivision")
    total_cost: Decimal = Field(alias="totalCost")
    participant_shares: list[ParticipantShareResponse] = Field(alias="participantShares")

class ParticipantShareUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")
    is_paying: bool = Field(alias="isPaying")
    amount: Decimal

class ExpenseUpdate(BaseModel):
    is_scanned: bool | None = Field(default=None, alias="isScanned")
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    payer_id: int | None = Field(default=None, alias="payerId")
    is_even_division: bool | None = Field(default=None, alias="isEvenDivision")
    total_cost: Decimal | None = Field(default=None, alias="totalCost")
    participant_shares: list[ParticipantShareUpdate] | None = Field(default=None, alias="participantShares")

class OweDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")
    user_name: str | None = Field(alias="userName")
    amount: str  # Using string for Decimal in JSON

class OweSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    owe_to_me: list[OweDetail] = Field(alias="oweToMe")
    i_owe_to: list[OweDetail] = Field(alias="iOweTo")

# class Expense(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, from_attributes=True)

#     id: int
#     is_scanned: bool = Field(alias="isScanned")
#     name: str = Field(max_length=100)
#     description: str = Field(max_length=500)
#     created_at: datetime = Field(alias="createdAt")
#     trip_id: int = Field(alias="tripId")
#     payer_id: int = Field(alias="payerId")
#     is_even_division: bool = Field(alias="isEvenDivision")
#     total_cost: Decimal = Field(alias="totalCost")

# class ExpenseCreate(BaseModel):
#     is_scanned: bool = Field(alias="isScanned")
#     name: str = Field(max_length=100)
#     description: str = Field(max_length=500)
#     payer_id: int = Field(alias="payerId")
#     is_even_division: bool = Field(alias="isEvenDivision")
#     total_cost: Decimal = Field(alias="totalCost")

# class ExpenseCreateResponse(BaseModel):
#     model_config = ConfigDict(populate_by_name=True)

#     id: int
#     is_scanned: bool = Field(alias="isScanned")
#     name: str = Field(max_length=100)
#     description: str = Field(max_length=500)
#     created_at: datetime = Field(alias="createdAt")
#     trip_id: int = Field(alias="tripId")
#     payer_id: int = Field(alias="payerId")
#     is_even_division: bool = Field(alias="isEvenDivision")
#     total_cost: Decimal = Field(alias="totalCost")

# class ExpenseUpdate(BaseModel):
#     is_scanned: bool | None = Field(default=None, alias="isScanned")
#     name: str | None = Field(default=None, max_length=100)
#     description: str | None = Field(default=None, max_length=500)
#     payer_id: int | None = Field(default=None, alias="payerId")
#     is_even_division: bool | None = Field(default=None, alias="isEvenDivision")
#     total_cost: Decimal | None = Field(default=None, alias="totalCost")

class FriendResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    user_id_1: int = Field(alias="userId1")
    user_id_2: int = Field(alias="userId2")
    is_accepted: bool = Field(alias="isAccepted")
    friend_username: str | None = Field(default=None, alias="friendUsername")

class FriendCreate(BaseModel):
    friend_id: int = Field(alias="friendId")

class FriendUser(BaseModel):
    """Schema for returning user info in friendlist"""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    username: str

class TripInviteResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    trip_id: int = Field(alias="tripId")
    invitee_id: int = Field(alias="inviteeId")
    inviter_id: int = Field(alias="inviterId")
    status: str
    created_at: datetime = Field(alias="createdAt")
    trip_name: str | None = Field(default=None, alias="tripName")
    invitee_username: str | None = Field(default=None, alias="inviteeUsername")
    inviter_username: str | None = Field(default=None, alias="inviterUsername")

class TripInviteCreate(BaseModel):
    invitee_id: int = Field(alias="inviteeId")

class TripInviteUpdate(BaseModel):
    status: str