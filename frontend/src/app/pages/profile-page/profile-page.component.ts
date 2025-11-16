import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../../core/services/auth.service';
import { UpperCasePipe } from '@angular/common'; 

@Component({
  selector: 'app-profile-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    UpperCasePipe,
  ],
  templateUrl: './profile-page.component.html',
  styleUrls: ['./profile-page.component.css']
})
export class ProfilePageComponent {
  private auth = inject(AuthService);
  user = this.auth.getCurrentUser() || { id: 0, username: '', email: '', isVerified: false };

  // Use username from backend response
  nickname = new FormControl<string>(this.user.username || '', { nonNullable: true });

  save() {
    console.log('profile save ->', {
      id: this.user.id,
      email: this.user.email,
      nickname: this.nickname.value,
    });
  }
}
