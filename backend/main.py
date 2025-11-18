from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
from datetime import timedelta
from schemas import *
from auth import authenticate_user, create_access_token, get_current_user, get_db, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from models import User, Trip as TripModel, Participant, Expense as ExpenseModel, Position
from email_utils import create_verification_token, verify_verification_token, send_verification_email


app = FastAPI()

prefix_router = APIRouter(prefix="/api")



# Enable CORS so your frontend can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@prefix_router.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

# Authentication endpoints
@prefix_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    - Email must be unique
    - Username must be unique
    - Password must be at least 8 characters
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    verification_token = create_verification_token(new_user.email)
    send_verification_email(new_user.email, new_user.username, verification_token)

    return new_user

@prefix_router.get("/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Email verification endpoint
    User clicks link in email with verification token
    """
    # Verify the token
    email = verify_verification_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already verified
    if user.is_verified:
        return {"message": "Email already verified"}

    # Mark as verified
    user.is_verified = True
    db.commit()

    return {"message": "Email successfully verified! You can now log in."}

@prefix_router.post("/resend-verification")
async def resend_verification(email_data: dict, db: Session = Depends(get_db)):
    """
    Resend verification email
    Body: {"email": "user@example.com"}
    """
    email = email_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )

    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal if user exists or not for security
        return {"message": "If the email exists, a verification link has been sent"}

    # Check if already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Send verification email
    verification_token = create_verification_token(user.email)
    send_verification_email(user.email, user.username, verification_token)

    return {"message": "Verification email sent"}

@prefix_router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint - accepts email and password as JSON
    Returns JWT access token
    Requires email to be verified
    """
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email and verify your account first."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@prefix_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user info - protected endpoint
    Requires valid JWT token in Authorization header: Bearer <token>
    """
    return current_user



# GET endpoint - retrieve data  ---- trip


@prefix_router.get("/trips/{trip_id}", response_model=Trip)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific trip by ID
    Only returns trip if current user is creator or participant
    """
    # Query the trip
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access (is creator or participant)
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    return trip

@prefix_router.get("/trips", response_model=list[Trip])
def get_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all trips for the current user
    Returns trips where user is creator or participant
    """
    # Get trips where user is creator
    creator_trips = db.query(TripModel).filter(
        TripModel.creator_id == current_user.id
    ).all()

    # Get trips where user is participant
    participant_trip_ids = db.query(Participant.trip_id).filter(
        Participant.user_id == current_user.id
    ).all()
    participant_trip_ids = [t[0] for t in participant_trip_ids]

    participant_trips = db.query(TripModel).filter(
        TripModel.id.in_(participant_trip_ids)
    ).all() if participant_trip_ids else []

    # Combine and deduplicate (in case user is both creator and participant)
    all_trips = {trip.id: trip for trip in creator_trips + participant_trips}

    return list(all_trips.values())

@prefix_router.post("/trips", response_model=TripCreateResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new trip
    Current user becomes the creator
    Participants are added from the request
    """
    # Create the trip
    new_trip = TripModel(
        name=data.name,
        description=data.description,
        creator_id=current_user.id
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    # Add participants
    for participant_id in data.participants:
        # Verify participant exists
        participant_user = db.query(User).filter(User.id == participant_id).first()
        if not participant_user:
            # Rollback and raise error
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id {participant_id} not found"
            )

        # Create participant relationship
        participant = Participant(
            user_id=participant_id,
            trip_id=new_trip.id
        )
        db.add(participant)

    db.commit()
    db.refresh(new_trip)

    return new_trip

@prefix_router.put("/trips/{trip_id}", response_model=Trip)
def update_trip(
    trip_id: int,
    data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing trip
    Only the creator can update the trip
    Can update name, description, dates, and participants
    """
    # Query the trip
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user is the creator
    if trip.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trip creator can update the trip"
        )

    # Update trip fields if provided
    if data.name is not None:
        trip.name = data.name
    if data.description is not None:
        trip.description = data.description
    if data.beginning_date is not None:
        trip.beginning_date = data.beginning_date
    if data.end_date is not None:
        trip.end_date = data.end_date

    # Update participants if provided
    if data.participants is not None:
        # Remove all existing participants
        db.query(Participant).filter(Participant.trip_id == trip_id).delete()

        # Add new participants
        for participant_id in data.participants:
            # Verify participant exists
            participant_user = db.query(User).filter(User.id == participant_id).first()
            if not participant_user:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with id {participant_id} not found"
                )

            # Create participant relationship
            participant = Participant(
                user_id=participant_id,
                trip_id=trip_id
            )
            db.add(participant)

    db.commit()
    db.refresh(trip)

    return trip

@prefix_router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a trip
    Only the creator can delete the trip
    Deletes all associated participants and expenses
    """
    # Query the trip
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user is the creator
    if trip.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the trip creator can delete the trip"
        )

    # Delete the trip (cascade will handle participants and expenses)
    db.delete(trip)
    db.commit()

    return None



@prefix_router.get("/trips/{trip_id}/expenses", response_model=list[Expense])
def get_expenses(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all expenses for a specific trip
    Only returns expenses if current user has access to the trip
    """
    # First verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Get all expenses for this trip
    expenses = db.query(ExpenseModel).filter(
        ExpenseModel.trip_id == trip_id
    ).all()

    return expenses


@prefix_router.post("/trips/{trip_id}/expenses", response_model=ExpenseCreateResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    trip_id: int,
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new expense for a trip
    Only allowed if current user has access to the trip
    """
    # Verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Verify payer exists and is part of the trip
    payer = db.query(User).filter(User.id == data.payer_id).first()
    if not payer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payer with id {data.payer_id} not found"
        )

    # Check if payer is creator or participant of the trip
    payer_is_creator = trip.creator_id == data.payer_id
    payer_is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == data.payer_id
    ).first() is not None

    if not payer_is_creator and not payer_is_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payer must be a participant of the trip"
        )

    # Create the expense
    new_expense = ExpenseModel(
        is_scanned=data.is_scanned,
        name=data.name,
        description=data.description,
        trip_id=trip_id,
        payer_id=data.payer_id,
        is_even_division=data.is_even_division,
        total_cost=data.total_cost
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense

@prefix_router.put("/trips/{trip_id}/expenses/{expense_id}", response_model=Expense)
def update_expense(
    trip_id: int,
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing expense
    Only allowed if current user has access to the trip
    Can update all expense fields except trip_id
    """
    # Verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Query the expense
    expense = db.query(ExpenseModel).filter(
        ExpenseModel.id == expense_id,
        ExpenseModel.trip_id == trip_id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Update expense fields if provided
    if data.is_scanned is not None:
        expense.is_scanned = data.is_scanned
    if data.name is not None:
        expense.name = data.name
    if data.description is not None:
        expense.description = data.description
    if data.beginning_date is not None:
        expense.beginning_date = data.beginning_date
    if data.end_date is not None:
        expense.end_date = data.end_date
    if data.is_even_division is not None:
        expense.is_even_division = data.is_even_division
    if data.total_cost is not None:
        expense.total_cost = data.total_cost

    # Update payer if provided
    if data.payer_id is not None:
        # Verify payer exists and is part of the trip
        payer = db.query(User).filter(User.id == data.payer_id).first()
        if not payer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payer with id {data.payer_id} not found"
            )

        # Check if payer is creator or participant of the trip
        payer_is_creator = trip.creator_id == data.payer_id
        payer_is_participant = db.query(Participant).filter(
            Participant.trip_id == trip_id,
            Participant.user_id == data.payer_id
        ).first() is not None

        if not payer_is_creator and not payer_is_participant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payer must be a participant of the trip"
            )

        expense.payer_id = data.payer_id

    db.commit()
    db.refresh(expense)

    return expense

@prefix_router.delete("/trips/{trip_id}/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    trip_id: int,
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an expense
    Only allowed if current user has access to the trip
    """
    # Verify the trip exists and user has access
    trip = db.query(TripModel).filter(TripModel.id == trip_id).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

    # Check if user has access to this trip
    is_creator = trip.creator_id == current_user.id
    is_participant = db.query(Participant).filter(
        Participant.trip_id == trip_id,
        Participant.user_id == current_user.id
    ).first() is not None

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this trip"
        )

    # Query the expense
    expense = db.query(ExpenseModel).filter(
        ExpenseModel.id == expense_id,
        ExpenseModel.trip_id == trip_id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Delete the expense
    db.delete(expense)
    db.commit()

    return None

app.include_router(prefix_router)



# Run the server when file is executed
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Makes server accessible externally
        port=8000,
        reload=True  # Auto-reload on code changes
    )