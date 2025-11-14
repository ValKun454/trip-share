from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
from datetime import timedelta
from schemas import *
from auth import authenticate_user, create_access_token, get_current_user, get_db, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from models import User
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


@prefix_router.get("/trips/{trip_id}")
def get_trip(trip_id: int):
    return {"id": trip_id, "name": "Sample Trip"}

@prefix_router.get("/trips")
def get_trips():
    return [
    {"id": 1, "name": "Sample Trip 1"},
    {"id": 2, "name": "Sample Trip 2"},
    {"id": 3, "name": "Sample Trip 3"},
    {"id": 4, "name": "Sample Trip 4"},
    {"id": 5, "name": "Sample Trip 5"}
    ]





@prefix_router.post("/trips", response_model=TripCreateResponse, status_code=201)
def create_trip(data: TripCreate):
    return {"tripId": 123, "name": data.name, 'dates': data.dates, 'participants': data.participants}

@prefix_router.get("/trips/{trip_id}/expenses")
def get_expenses(trip_id: int):
    return [
    {"id": 1,"tripId": trip_id , "title": "Sample Expense"},
    {"id": 2,"tripId": trip_id , "title": "Sample Expense 2"}
    ]



@prefix_router.post("/trips/{trip_id}/expenses", response_model=ExpenseCreateResponse, status_code=201)
def create_expense(data: ExpenseCreate):
    return {
        'id': 456,
        'tripId': data.trip_id,
        'title': data.title,
        'amount': data.amount,
        'paidBy': data.paid_by,
        'included': data.included
    }

app.include_router(prefix_router)



# Run the server when file is executed
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Makes server accessible externally
        port=8000,
        reload=True  # Auto-reload on code changes
    )



"""  // poezdki
  getTrips(): Observable<Trip[]> { ----- done 
    return this.http.get<Trip[]>(`${this.base}/trips`);
  }
  getTrip(id: string): Observable<Trip> { ---- done
    return this.http.get<Trip>(`${this.base}/trips/${id}`);
  }
  createTrip(dto: CreateTripDto): Observable<Trip> {
    return this.http.post<Trip>(`${this.base}/trips`, dto);
  }

  // traty
  getExpenses(tripId: string): Observable<Expense[]> {
    return this.http.get<Expense[]>(`${this.base}/trips/${tripId}/expenses`);
  }
  createExpense(tripId: string, exp: Omit<Expense, 'id'|'tripId'>): Observable<Expense> {
    return this.http.post<Expense>(`${this.base}/trips/${tripId}/expenses`, exp);
  }
}
"""