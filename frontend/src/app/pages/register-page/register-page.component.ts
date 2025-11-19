import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-register-page',
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
  templateUrl: './register-page.component.html',
  styleUrls: ['./register-page.component.css']
})
export class RegisterPageComponent {
  form: FormGroup;
  isLoading = false;
  serverError: string | null = null;
  successInfo: { email: string } | null = null;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private api: ApiService
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      // backend: username is REQUIRED (min 3, max 50)
      username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      // backend: password min 8
      password: ['', [Validators.required, Validators.minLength(8)]],
    });
  }

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.isLoading = true;
    this.serverError = null;
    this.successInfo = null;

    const payload = this.form.value as { email:string; username:string; password:string };

    this.api.register(payload).subscribe({
      next: () => {
        this.isLoading = false;

        // Zapisujemy dane do automatycznego logowania:
        // będą użyte tylko raz po przejściu na stronę logowania.
        localStorage.setItem('preAuthEmail', payload.email);
        localStorage.setItem('preAuthPassword', payload.password);

        // pokazujemy info o weryfikacji
        this.successInfo = { email: payload.email };
        this.form.disable();
      },
      error: (err) => {
        this.isLoading = false;
        const detail = err?.error?.detail || '';
        if (detail) {
          this.serverError = detail; // "Email already registered" / "Username already taken"
        } else {
          this.serverError = 'Registration failed. Please try again.';
        }
      }
    });
  }

  resend() {
    const email = this.form.get('email')?.value;
    if (!email) return;
    this.api.resendVerification(email).subscribe({
      next: () => {},
      error: () => {}
    });
  }

  goLogin() {
    // przejście do logowania – formularz logowania odczyta dane z localStorage
    this.router.navigateByUrl('/login');
  }
}
