import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-auth-layout',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <div class="auth-layout">
      <div class="auth-container">
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
  styleUrls: ['./auth-layout.component.css']
})
export class AuthLayoutComponent {}