import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private router = inject(Router);
  private isLoggedInSubject = new BehaviorSubject<boolean>(this.hasToken());
  
  isLoggedIn$: Observable<boolean> = this.isLoggedInSubject.asObservable();

  constructor() {
    // For demo purposes, auto-login a mock user if no token exists
    if (!this.hasToken()) {
      this.setMockUser();
    }
  }

  private setMockUser(): void {
    const mockUser = { username: 'Demo User', loginTime: new Date() };
    localStorage.setItem('authToken', 'demo-token');
    localStorage.setItem('currentUser', JSON.stringify(mockUser));
    this.isLoggedInSubject.next(true);
  }

  private hasToken(): boolean {
    // Check if user has authentication token
    return !!localStorage.getItem('authToken');
  }

  login(username: string, password: string): Observable<boolean> {
    // Simulate login - replace with actual API call
    const success = !!(username && password); // Basic validation
    if (success) {
      localStorage.setItem('authToken', 'mock-jwt-token');
      localStorage.setItem('currentUser', JSON.stringify({ username, loginTime: new Date() }));
      this.isLoggedInSubject.next(true);
    }
    return new BehaviorSubject(success).asObservable();
  }

  logout(): void {
    // Clear authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    this.isLoggedInSubject.next(false);
    
    // Navigate to login page
    this.router.navigate(['/login']);
  }

  getCurrentUser(): any {
    const userStr = localStorage.getItem('currentUser');
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated(): boolean {
    return this.hasToken();
  }
}