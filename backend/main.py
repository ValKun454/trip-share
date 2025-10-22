from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

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



# GET endpoint - retrieve data  ---- trip 
@prefix_router.get("/trips/{trip_id}")
def get_trip(trip_id: int):
    return {"trip_id": trip_id, "title": "Sample Trip", "description": "This is a sample trip."}

@prefix_router.get("/trips/")
def get_trips():
    return [
    {"trip_id": 1, "title": "Sample Trip 1", "description": "This is a sample trip. 1"},
    {"trip_id": 2, "title": "Sample Trip 2", "description": "This is a sample trip. 2"},
    {"trip_id": 3, "title": "Sample Trip 3", "description": "This is a sample trip. 3"},
    {"trip_id": 4, "title": "Sample Trip 4", "description": "This is a sample trip. 4"},
    {"trip_id": 5, "title": "Sample Trip 5", "description": "This is a sample trip. 5"}
    ]


class TripCreate(BaseModel):
    title: str
    description: str = None
    dates: str
    participants: list[str]

class TripCreateResponse(BaseModel):
    trip_id: int
    title: str
    description: str = None
    dates: str
    participants: list[str]


@prefix_router.post("/trips/create")
def create_trip(data: TripCreate, response_model=TripCreateResponse, status_code=201):
    return {"trip_id": 123, "title": data.title, "description": data.description, 'dates': data.dates, 'participants': data.participants}

@prefix_router.get("/expenses/")
def get_expenses():
    return [
    {"id": 1,"trip_id": 1, "title": "Sample Expense", "description": "This is a sample trip."}
    ]

class ExpenseCreate(BaseModel):
    trip_id: int
    title: str
    amount: float
    paid_by: str
    participants: list[str]

class ExpenseCreateResponse(BaseModel):
    id: int
    trip_id: int
    title: str
    amount: float
    paid_by: str
    participants: list[str]

@prefix_router.post("/expenses/create")
def create_expense(data: ExpenseCreate, response_model=ExpenseCreateResponse, status_code=201):
    return {
        'id': 456,
        'trip_id': data.trip_id,
        'title': data.title,
        'amount': data.amount,
        'paid_by': data.paid_by,
        'participants': data.participants
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