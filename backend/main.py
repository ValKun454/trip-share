from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
from datetime import timedelta
from schemas import *
from auth import authenticate_user, create_access_token, get_current_user, get_db, ACCESS_TOKEN_EXPIRE_MINUTES
from models import User


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
@prefix_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login endpoint - accepts email (as username) and password
    Returns JWT access token
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@prefix_router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user info - protected endpoint
    Requires valid JWT token
    """
    return {"email": current_user.email, "id": current_user.id}



# GET endpoint - retrieve data  ---- trip 


@prefix_router.get("/trips/{trip_id}")
def get_trip(trip_id: int):
    return {"id": trip_id, "name": "Sample Trip"}

@prefix_router.get("/trips/")
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