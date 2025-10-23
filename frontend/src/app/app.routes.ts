import { Routes } from '@angular/router';

import { TripsPageComponent } from './pages/trips-page/trips-page.component';
import { SettingsPageComponent } from './pages/settings-page/settings-page.component';
import { NotFoundPageComponent } from './pages/not-found-page/not-found-page.component';
import { ContactUsPageComponent } from './pages/contact-us-page/contact-us-page.component';
import { LoginPageComponent } from './pages/login-page/login-page.component';
import { RegisterPageComponent } from './pages/register-page/register-page.component';
import { AuthLayoutComponent } from './layout/auth-layout/auth-layout.component';
import { ShellComponent } from './layout/shell/shell.component';

export const routes: Routes = [
  // Authentication routes (without shell)
  {
    path: 'auth',
    component: AuthLayoutComponent,
    children: [
      { path: 'login', component: LoginPageComponent, title: 'Login - TripShare' },
      { path: 'register', component: RegisterPageComponent, title: 'Register - TripShare' }
    ]
  },
  
  // Redirect root to login initially (can be changed to redirect to trips if user is authenticated)
  { path: '', redirectTo: '/auth/login', pathMatch: 'full' },
  
  // Redirect old login/register routes
  { path: 'login', redirectTo: '/auth/login' },  
  { path: 'register', redirectTo: '/auth/register' },
  
  // Main application routes (with shell) - moved to separate path
  {
    path: 'app',
    component: ShellComponent,
    children: [
      { path: '', redirectTo: 'trips', pathMatch: 'full' },
      { path: 'trips', component: TripsPageComponent, title: 'Trips - TripShare' },
      { path: 'settings', component: SettingsPageComponent, title: 'Settings - TripShare' },
      { path: 'contact', component: ContactUsPageComponent, title: 'Contact Us - TripShare' },
    ]
  },
  
  // 404 page
  { path: '**', component: NotFoundPageComponent, title: 'Not Found - TripShare' },
];