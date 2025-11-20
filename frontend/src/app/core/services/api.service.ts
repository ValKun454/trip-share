import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GetTrip, CreateTrip } from '../models/trip.model'
import { Expense, ExpenseCreate } from '../models/expense.model'
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
    return this.http.get<GetTrip[]>(`${this.base}/trips`, this.getAuthHeaders());
  }
  getTrip(id: number): Observable<GetTrip> {
    return this.http.get<GetTrip>(`${this.base}/trips/${id}`, this.getAuthHeaders());
  }
  /**
   * Create trip - send snake_case field names expected by backend
   * Backend schema TripCreate: { name, description, participants }
   */
  createTrip(dto: CreateTrip): Observable<any> {
    const payload = {
      name: dto.name,
      description: dto.description || '',
      participants: dto.participants || []
    };
    return this.http.post<any>(`${this.base}/trips`, payload, this.getAuthHeaders());
  }

  /**
   * Update trip - send snake_case field names expected by backend
   * Backend schema TripUpdate: { name, description, beginning_date, end_date, participants }
   */
  updateTrip(tripId: number, dto: any): Observable<GetTrip> {
    const payload: any = {
      name: dto.name || undefined,
      description: dto.description || undefined,
      beginning_date: dto.beginningDate || undefined,
      end_date: dto.endDate || undefined,
      participants: dto.participants || undefined
    };
    // Remove undefined values
    Object.keys(payload).forEach(key => payload[key] === undefined && delete payload[key]);
    return this.http.put<GetTrip>(`${this.base}/trips/${tripId}`, payload, this.getAuthHeaders());
  }

  /**
   * Delete trip
   */
  deleteTrip(tripId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/trips/${tripId}`, this.getAuthHeaders());
  }

  // Friends endpoints
  /**
   * Get all friends for current user
   */
  getFriends(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/friends`, this.getAuthHeaders());
  }

  /**
   * Add a friend by user ID
   */
  addFriend(friendId: number): Observable<any> {
    const payload = { friendId: friendId };
    return this.http.post<any>(`${this.base}/friends`, payload, this.getAuthHeaders());
  }

  /**
   * Remove a friend by user ID
   */
  removeFriend(friendId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/friends/${friendId}`, this.getAuthHeaders());
  }

  // traty
  getExpenses(tripId: number): Observable<Expense[]> {
    return this.http.get<Expense[]>(`${this.base}/trips/${tripId}/expenses`, this.getAuthHeaders());
  }
  /**
   * Create expense - send snake_case field names expected by backend
   * Backend schema ExpenseCreate: { is_scanned, name, description, payer_id, is_even_division, total_cost }
   */
  createExpense(tripId: number, exp: ExpenseCreate): Observable<Expense> {
    const payload = {
      is_scanned: exp.isScanned,
      name: exp.name,
      description: exp.description || '',
      payer_id: exp.payerId,
      is_even_division: exp.isEvenDivision,
      total_cost: exp.totalCost
    };
    return this.http.post<Expense>(`${this.base}/trips/${tripId}/expenses`, payload, this.getAuthHeaders());
  }

  // identyfikujemy usera po UID
  getDebtsSummaryByUid(uid: string): Observable<DebtsSummary> {
    return this.http.get<DebtsSummary>(`${this.base}/debts/summary?uid=${encodeURIComponent(uid)}`, this.getAuthHeaders());
  }

  // Trip summary endpoint (expected to return settlement / summary data for a trip)
  getTripSummary(tripId: string): Observable<any> {
    return this.http.get<any>(`${this.base}/trips/${encodeURIComponent(tripId)}/summary`, this.getAuthHeaders());
  }
}
