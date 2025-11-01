import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GetTrip, CreateTrip } from '../models/trip.model'
import { Expense } from '../models/expense.model'
import { DebtsSummary } from '../models/debts.model';

// dannye parni derzjite krepko ne poteryaite


@Injectable({ providedIn: 'root' })
export class ApiService {
  // chatgpt skazal eto baza
  private base = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  // poezdki
  getTrips(): Observable<GetTrip[]> {
    return this.http.get<GetTrip[]>(`${this.base}/trips`);
  }
  getTrip(id: string): Observable<GetTrip> {
    return this.http.get<GetTrip>(`${this.base}/trips/${id}`);
  }
  createTrip(dto: CreateTrip): Observable<GetTrip> {
    return this.http.post<GetTrip>(`${this.base}/trips`, dto);
  }

  // traty
  getExpenses(tripId: string): Observable<Expense[]> {
    return this.http.get<Expense[]>(`${this.base}/trips/${tripId}/expenses`);
  }
  createExpense(tripId: string, exp: Omit<Expense, 'id'|'tripId'>): Observable<Expense> {
    return this.http.post<Expense>(`${this.base}/trips/${tripId}/expenses`, exp);
  }

  // identyfikujemy usera po UID
  getDebtsSummaryByUid(uid: string): Observable<DebtsSummary> {
    return this.http.get<DebtsSummary>(`${this.base}/debts/summary?uid=${encodeURIComponent(uid)}`);
  }
}
