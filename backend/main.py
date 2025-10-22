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
class Trip(BaseModel):
    id: str
    name: str
    dates: str
    participants: list[str]

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


class TripCreate(BaseModel):   # TODO: maybe add id as optional field later and delete second object TripCreateResponse
    name: str
    dates: str
    participants: list[str]

class TripCreateResponse(BaseModel):
    trip_id: int
    name: str
    dates: str
    participants: list[str]


@prefix_router.post("/trips", response_model=TripCreateResponse, status_code=201)
def create_trip(data: TripCreate):
    return {"tripId": 123, "name": data.name, 'dates': data.dates, 'participants': data.participants}

@prefix_router.get("/trips/{trip_id}/expenses")
def get_expenses(trip_id: int):
    return [
    {"id": 1,"tripId": trip_id , "title": "Sample Expense"},
    {"id": 2,"tripId": trip_id , "title": "Sample Expense 2"}
    ]

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