import { Routes } from '@angular/router';

import { TripsPageComponent } from './pages/trips-page/trips-page.component';
import { TripDetailPageComponent } from './pages/trip-detail-page/trip-detail-page.component';
import { ExpensesSummaryPageComponent } from './pages/expenses-summary-page/expenses-summary-page.component';
import { ProfilePageComponent } from './pages/profile-page/profile-page.component';
import { NotFoundPageComponent } from './pages/not-found-page/not-found-page.component';
import { ContactUsPageComponent } from './pages/contact-us-page/contact-us-page.component';
import { FriendsPageComponent } from './pages/friends-page/friends-page.component';
import { LoginPageComponent } from './pages/login-page/login-page.component';
import { RegisterPageComponent } from './pages/register-page/register-page.component';
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

  // NEW: rejestracja w tym samym layoucie auth
  {
    path: 'register',
    component: AuthLayoutComponent,
    canActivate: [noAuthGuard],
    children: [
      { path: '', component: RegisterPageComponent, title: 'Register' }
    ]
  },

  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: 'trips', component: TripsPageComponent, title: 'Trips' },
      { path: 'trips/:id', component: TripDetailPageComponent, title: 'Trip Details' },
      { path: 'expenses', component: ExpensesSummaryPageComponent, title: 'Total Expenses' },
      { path: 'profile', component: ProfilePageComponent, title: 'Profile' },
      { path: 'friends', component: FriendsPageComponent, title: 'Friends' },
      { path: 'contact', component: ContactUsPageComponent, title: 'Contact Us' },
    ]
  },
  { path: '**', component: NotFoundPageComponent, title: 'Not Found' },
];