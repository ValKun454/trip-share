import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule, UpperCasePipe } from '@angular/common';
import { AuthService } from '../../core/services/auth.service';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-profile-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    UpperCasePipe,
    CommonModule,
  ],
  templateUrl: './profile-page.component.html',
  styleUrls: ['./profile-page.component.css']
})
export class ProfilePageComponent {
  private auth = inject(AuthService);
  private api = inject(ApiService);
  
  user = this.auth.getCurrentUser() || { id: 0, username: '', email: '', isVerified: false };
  nickname = new FormControl<string>(this.user.username || '', { nonNullable: true });
  
  saving = false;
  error: string | null = null;
  successMessage: string | null = null;

  save() {
    if (this.nickname.invalid || this.nickname.pristine) {
      return;
    }

    this.saving = true;
    this.error = null;
    this.successMessage = null;

    const newUsername = this.nickname.value;

    // Call API to update username
    this.api.updateMe({ username: newUsername }).subscribe({
      next: (updatedUser) => {
        // Update local user data
        this.user.username = updatedUser.username;
        
        // Update auth service's stored user
        this.auth.setCurrentUser(updatedUser);
        
        // Mark form as pristine so button disables
        this.nickname.markAsPristine();
        
        this.successMessage = 'Username updated successfully!';
        this.saving = false;
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          this.successMessage = null;
        }, 3000);
      },
      error: (e) => {
        console.error('Failed to update username', e);
        let errorMsg = 'Failed to update username';
        
        if (typeof e?.error?.detail === 'string') {
          errorMsg = e.error.detail;
        } else if (e?.error?.message) {
          errorMsg = e.error.message;
        } else if (e?.message) {
          errorMsg = e.message;
        }
        
        this.error = errorMsg;
        this.saving = false;
      }
    });
  }
}
