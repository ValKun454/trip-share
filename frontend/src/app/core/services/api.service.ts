import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { GetTrip, CreateTrip } from '../models/trip.model';
import { Expense, ExpenseCreate } from '../models/expense.model';
import { DebtsSummary } from '../models/debts.model';
import { Router } from '@angular/router';
import { TripInvite } from '../models/trip-invite.model';

// dannye parni derzjite krepko ne poteryaite

@Injectable({ providedIn: 'root' })
export class ApiService {
  // chatgpt skazal eto baza
  private base = 'http://localhost:8000/api';

  constructor(private http: HttpClient, private router: Router) {}

  private getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return { headers };
  }

  private handleAuthError<T>(obs: Observable<T>): Observable<T> {
    return obs.pipe(
      catchError((error: any) => {
        if (error && error.status === 401) {
          localStorage.removeItem('authToken');
          this.router.navigate(['/login']);
        }
        return throwError(() => error);
      })
    );
  }

  // Authentication
  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.base}/login`, { email, password });
  }

  getMe(): Observable<any> {
    return this.handleAuthError(
      this.http.get(`${this.base}/me`, this.getAuthHeaders())
    );
  }

  /**
   * Update current user's information
   * Can update username, email, or password
   * Expects snake_case field names: { username, email, password }
   */
  updateMe(data: any): Observable<any> {
    const payload: any = {};
    if (data.username !== undefined) payload.username = data.username;
    if (data.email !== undefined) payload.email = data.email;
    if (data.password !== undefined) payload.password = data.password;

    return this.handleAuthError(
      this.http.put(`${this.base}/me`, payload, this.getAuthHeaders())
    );
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
    return this.handleAuthError(
      this.http.get<GetTrip[]>(`${this.base}/trips`, this.getAuthHeaders())
    );
  }

  getTrip(id: number): Observable<GetTrip> {
    return this.handleAuthError(
      this.http.get<GetTrip>(`${this.base}/trips/${id}`, this.getAuthHeaders())
    );
  }

  /**
   * Create trip - send snake_case field names expected by backend
   */
  createTrip(dto: CreateTrip): Observable<any> {
    const payload = {
      name: dto.name,
      description: dto.description || '',
      participants: dto.participants || []
    };
    return this.handleAuthError(
      this.http.post<any>(`${this.base}/trips`, payload, this.getAuthHeaders())
    );
  }

  /**
   * Update trip - send snake_case field names expected by backend
   */
  updateTrip(tripId: number, dto: any): Observable<GetTrip> {
    const payload: any = {
      name: dto.name || undefined,
      description: dto.description || undefined,
      beginning_date: dto.beginningDate || undefined,
      end_date: dto.endDate || undefined,
      participants: dto.participants || undefined
    };
    Object.keys(payload).forEach(key => payload[key] === undefined && delete payload[key]);
    return this.handleAuthError(
      this.http.put<GetTrip>(`${this.base}/trips/${tripId}`, payload, this.getAuthHeaders())
    );
  }

  /**
   * Delete trip
   */
  deleteTrip(tripId: number): Observable<void> {
    return this.handleAuthError(
      this.http.delete<void>(`${this.base}/trips/${tripId}`, this.getAuthHeaders())
    );
  }

  // Friends endpoints

  getFriends(): Observable<any[]> {
    return this.handleAuthError(
      this.http.get<any[]>(`${this.base}/friends`, this.getAuthHeaders())
    );
  }

  getFriendRequests(): Observable<any[]> {
    return this.handleAuthError(
      this.http.get<any[]>(`${this.base}/friends/requests`, this.getAuthHeaders())
    );
  }

  addFriend(friendId: number): Observable<any> {
    const payload = { friendId: friendId };
    return this.handleAuthError(
      this.http.post<any>(`${this.base}/friends`, payload, this.getAuthHeaders())
    );
  }

  acceptFriendRequest(friendshipId: number): Observable<any> {
    return this.handleAuthError(
      this.http.put<any>(`${this.base}/friends/${friendshipId}/accept`, {}, this.getAuthHeaders())
    );
  }

  removeFriend(friendId: number): Observable<void> {
    return this.handleAuthError(
      this.http.delete<void>(`${this.base}/friends/${friendId}`, this.getAuthHeaders())
    );
  }

  // traty
  getExpenses(tripId: number): Observable<Expense[]> {
    return this.handleAuthError(
      this.http.get<Expense[]>(`${this.base}/trips/${tripId}/expenses`, this.getAuthHeaders())
    );
  }

  /**
   * Create expense
   */
  createExpense(tripId: number, exp: ExpenseCreate): Observable<Expense> {
    const payload = {
      isScanned: exp.isScanned,
      name: exp.name,
      description: exp.description || '',
      payerId: exp.payerId,
      isEvenDivision: exp.isEvenDivision,
      totalCost: exp.totalCost
    };
    return this.handleAuthError(
      this.http.post<Expense>(`${this.base}/trips/${tripId}/expenses`, payload, this.getAuthHeaders())
    );
  }

  // identyfikujemy usera po UID
  getDebtsSummaryByUid(uid: string): Observable<DebtsSummary> {
    return this.handleAuthError(
      this.http.get<DebtsSummary>(`${this.base}/debts/summary?uid=${encodeURIComponent(uid)}`, this.getAuthHeaders())
    );
  }

  // Trip summary endpoint
  getTripSummary(tripId: string): Observable<any> {
    return this.handleAuthError(
      this.http.get<any>(`${this.base}/trips/${encodeURIComponent(tripId)}/summary`, this.getAuthHeaders())
    );
  }

  // Zaproszenia do wyjazdów - lista przychodzących zaproszeń
  getTripInvites(): Observable<TripInvite[]> {
    return this.handleAuthError(
      this.http.get<TripInvite[]>(`${this.base}/trips/invites`, this.getAuthHeaders())
    );
  }

  // Wysłanie zaproszenia do wyjazdu (trip)
  inviteUserToTrip(tripId: number, inviteeId: number): Observable<TripInvite> {
    const payload = { inviteeId };
    return this.handleAuthError(
      this.http.post<TripInvite>(`${this.base}/trips/${tripId}/invites`, payload, this.getAuthHeaders())
    );
  }

  // Odpowiedź na zaproszenie do wyjazdu (zaakceptuj / odrzuć)
  respondToTripInvite(inviteId: number, status: 'accepted' | 'declined'): Observable<TripInvite> {
    return this.handleAuthError(
      this.http.put<TripInvite>(`${this.base}/trips/invites/${inviteId}`, { status }, this.getAuthHeaders())
    );
  }
}
