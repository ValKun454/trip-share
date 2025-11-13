import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap, of, map, catchError, throwError } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private router = inject(Router);
  private api = inject(ApiService);

  private isLoggedInSubject = new BehaviorSubject<boolean>(this.hasToken());

  isLoggedIn$: Observable<boolean> = this.isLoggedInSubject.asObservable();

  constructor() {}

  private hasToken(): boolean {
    // Check if user has authentication token
    return !!localStorage.getItem('authToken');
  }

  /**
   * Call backend to login. On success store token and current user.
   * Expects backend POST /api/login { email, password } -> { access_token, token_type }
   */
  login(email: string, password: string): Observable<boolean> {
    if (!email || !password) {
      return of(false);
    }
    return this.api.login(email, password).pipe(
      tap((res: any) => {
        const token = res?.access_token || res?.accessToken || res?.accessToken;
        if (token) {
          localStorage.setItem('authToken', token);
          // fetch current user but don't block
          this.api.getMe().subscribe({
            next: (user) => localStorage.setItem('currentUser', JSON.stringify(user)),
            error: () => {}
          });
          this.isLoggedInSubject.next(true);
          this.router.navigate(['/trips']);
        }
      }),
      map((res: any) => {
        const token = res?.access_token || res?.accessToken || res?.accessToken;
        return !!token;
      }),
      catchError((err) => {
        // propagate error to caller so UI can display messages
        return throwError(() => err);
      })
    );
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