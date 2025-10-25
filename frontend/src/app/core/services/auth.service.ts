import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private router = inject(Router);
  private isLoggedInSubject = new BehaviorSubject<boolean>(this.hasToken());
  
  isLoggedIn$: Observable<boolean> = this.isLoggedInSubject.asObservable();

  constructor() {}

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
      this.router.navigate(['/trips']);
    }
    return new BehaviorSubject(success).asObservable();
  }

  /**
   * Temporary mock login helper for development/demos.
   * Sets a mock token and a demo user, then navigates to /trips.
   */
  loginAsDemo(): Observable<boolean> {
    const demoUser = { username: 'demo', loginTime: new Date() };
    localStorage.setItem('authToken', 'mock-jwt-token');
    localStorage.setItem('currentUser', JSON.stringify(demoUser));
    this.isLoggedInSubject.next(true);
    this.router.navigate(['/trips']);
    return new BehaviorSubject(true).asObservable();
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