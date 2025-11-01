import { Routes } from '@angular/router';

import { TripsPageComponent } from './pages/trips-page/trips-page.component';
import { ProfilePageComponent } from './pages/profile-page/profile-page.component';
import { NotFoundPageComponent } from './pages/not-found-page/not-found-page.component';
import { ContactUsPageComponent } from './pages/contact-us-page/contact-us-page.component';
import { LoginPageComponent } from './pages/login-page/login-page.component';
import { ShellComponent } from './layout/shell/shell.component';
import { AuthLayoutComponent } from './layout/auth-layout/auth-layout.component';
import { authGuard, noAuthGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { 
    path: '', 
    pathMatch: 'full', 
    redirectTo: 'login' 
  },
  {
    path: 'login',
    component: AuthLayoutComponent,
    canActivate: [noAuthGuard],
    children: [
      { path: '', component: LoginPageComponent, title: 'Login' }
    ]
  },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: 'trips', component: TripsPageComponent, title: 'Trips' },
      { path: 'profile', component: ProfilePageComponent, title: 'Profile' },
      { path: 'contact', component: ContactUsPageComponent, title: 'Contact Us' },
    ]
  },
  { path: '**', component: NotFoundPageComponent, title: 'Not Found' },
];