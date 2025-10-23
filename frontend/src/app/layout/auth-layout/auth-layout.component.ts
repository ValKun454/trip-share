import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-auth-layout',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <div class="auth-layout">
      <div class="auth-background">
        <div class="auth-overlay"></div>
      </div>
      <div class="auth-content">
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
  styles: [`
    .auth-layout {
      height: 100vh;
      width: 100vw;
      position: relative;
      overflow: hidden;
    }

    .auth-background {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background:
        radial-gradient(900px 480px at 78% -10%, color-mix(in srgb, var(--primary) 18%, transparent) 0%, transparent 68%),
        linear-gradient(180deg, var(--bg) 0%, #0a0f15 100%);
      background-attachment: fixed;
    }

    .auth-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.1);
    }

    .auth-content {
      position: relative;
      z-index: 1;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
  `]
})
export class AuthLayoutComponent {}