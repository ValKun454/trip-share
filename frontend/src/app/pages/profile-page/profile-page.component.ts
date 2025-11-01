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
  // pobranie usera (mock)
  private auth = inject(AuthService);
  user = this.auth.getCurrentUser() || { username: '', email: '', uid: '' };

  // kontrolka do nicku
  nickname = new FormControl<string>(this.user.username || '', { nonNullable: true });

  // symulacja zapisu
  save() {
    console.log('profile save ->', {
      email: this.user.email,
      nickname: this.nickname.value,
      uid: this.user.uid,
    });
  }
}
