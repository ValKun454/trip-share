import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// dannye parni derzjite krepko ne poteryaite
export interface Trip {
  id: string;
  name: string;
  dates: string;               
  participants: string[];      
}
export interface CreateTripDto {
  name: string;
  dates: string;
  participants?: string[];
}
export interface Expense {
  id: string;
  tripId: string;
  title: string;
  amount: number;              // raksy
  paidBy: string;              // user id/name
  included: string[];          // skolko?
  date: string;                // nu eto data
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  // chatgpt skazal eto baza
  private base = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  // poezdki
  getTrips(): Observable<Trip[]> {
    return this.http.get<Trip[]>(`${this.base}/trips`);
  }
  getTrip(id: string): Observable<Trip> {
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
