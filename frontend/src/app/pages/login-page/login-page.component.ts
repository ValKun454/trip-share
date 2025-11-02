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
  readonly DEMO_USERNAME = 'demo';
  readonly DEMO_PASSWORD = 'demo123';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router

  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required]]
    });
  }
  
  goRegister() {
    // nawigacja do rejestracji
    this.router.navigateByUrl('/register');
  }

  onLogin() {
    if (this.loginForm.valid) {
      const { username, password } = this.loginForm.value;
      this.authService.login(username, password).subscribe({
        next: (success) => {
          if (!success) {
            // Handle login error
            console.error('Login failed');
          }
        },
        error: (error) => {
          console.error('Login error:', error);
        }
      });
    }
  }

  fillDemo() {
    this.loginForm.setValue({ username: this.DEMO_USERNAME, password: this.DEMO_PASSWORD });
  }

  loginAsDemo() {
    this.authService.loginAsDemo().subscribe();
  }
}