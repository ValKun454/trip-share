import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../core/services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css']
})
export class LoginPageComponent implements OnInit {
  loginForm: FormGroup;
  isLoading = false;
  serverError: string | null = null;
  hidePassword = true;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router

  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    // Automatyczne uzupełnienie po rejestracji
    // Dane są zapisane w localStorage przez stronę rejestracji
    const preEmail = localStorage.getItem('preAuthEmail');
    const prePassword = localStorage.getItem('preAuthPassword');

    if (preEmail || prePassword) {
      this.loginForm.patchValue({
        email: preEmail ?? '',
        password: prePassword ?? ''
      });
      // Po jednorazowym użyciu czyścimy – to tylko pomoc UX, nie stałe dane
      localStorage.removeItem('preAuthEmail');
      localStorage.removeItem('preAuthPassword');
    }
  }

  goRegister() {
    // nawigacja do rejestracji
    this.router.navigateByUrl('/register');
  }

  togglePasswordVisibility() {
    this.hidePassword = !this.hidePassword;
  }

  onLogin() {
    if (!this.loginForm.valid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    const { email, password } = this.loginForm.value;
    this.isLoading = true;
    this.serverError = null;

    this.authService.login(email, password).subscribe({
      next: (success) => {
        this.isLoading = false;
        if (!success) {
          this.serverError = 'Login failed. Please check your credentials.';
        }
      },
      error: (error) => {
        this.isLoading = false;
        // Inspect HTTP error
        const status = error?.status;
        if (status === 401) {
          this.serverError = 'Incorrect email or password.';
        } else if (status === 403) {
          this.serverError = 'Email not verified. Please verify your email before logging in.';
        } else {
          this.serverError = error?.error?.detail || 'An unexpected error occurred. Please try again.';
        }
      }
    });
  }
}