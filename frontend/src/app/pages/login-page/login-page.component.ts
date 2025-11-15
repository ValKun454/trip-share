import { Component } from '@angular/core';
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
export class LoginPageComponent {
  loginForm: FormGroup;
  readonly DEMO_EMAIL = 'demo@example.com';
  readonly DEMO_PASSWORD = 'demo123';
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

  fillDemo() {
    this.loginForm.setValue({ email: this.DEMO_EMAIL, password: this.DEMO_PASSWORD });
  }

  loginAsDemo() {
    this.authService.loginAsDemo().subscribe();
  }
}