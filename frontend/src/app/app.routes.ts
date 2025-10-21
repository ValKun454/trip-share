import { Routes } from '@angular/router';

import { TripsPageComponent } from './pages/trips-page/trips-page.component';
import { SettingsPageComponent } from './pages/settings-page/settings-page.component';
import { NotFoundPageComponent } from './pages/not-found-page/not-found-page.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'trips' },
  { path: 'trips', component: TripsPageComponent, title: 'Trips' },
  { path: 'settings', component: SettingsPageComponent, title: 'Settings' },
  { path: '**', component: NotFoundPageComponent, title: 'Not Found' },
];