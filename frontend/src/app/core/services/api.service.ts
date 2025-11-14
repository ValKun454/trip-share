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

  private getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    const headers: Record<string,string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return { headers };
  }

  // Authentication
  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.base}/login`, { email, password });
  }

  getMe(): Observable<any> {
    return this.http.get(`${this.base}/me`, this.getAuthHeaders());
  }

  // register user, backend expects { email, username, password }
  register(payload: { email: string; username: string; password: string }): Observable<any> {
    return this.http.post(`${this.base}/register`, payload);
  }

  // resend verification mail 
  resendVerification(email: string): Observable<any> {
    return this.http.post(`${this.base}/resend-verification`, { email });
  }

  // verify email by token (GET /verify?token=...)
  verifyEmail(token: string): Observable<any> {
    return this.http.get(`${this.base}/verify`, { params: { token } });
  }

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

  // Trip summary endpoint (expected to return settlement / summary data for a trip)
  getTripSummary(tripId: string): Observable<any> {
    return this.http.get<any>(`${this.base}/trips/${encodeURIComponent(tripId)}/summary`);
  }
}
