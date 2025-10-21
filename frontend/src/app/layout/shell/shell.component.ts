import { Component, inject } from "@angular/core";
import { RouterOutlet, RouterLink, RouterLinkActive } from "@angular/router";
import { BreakpointObserver, Breakpoints } from "@angular/cdk/layout";
import { map } from "rxjs";
import { NgIf, AsyncPipe } from "@angular/common";

import { MatSidenavModule } from "@angular/material/sidenav";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";
import { MatListModule } from "@angular/material/list";
import { MatButtonModule } from "@angular/material/button";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [
    RouterOutlet, RouterLink, RouterLinkActive, NgIf, AsyncPipe,
    MatSidenavModule, MatToolbarModule, MatIconModule, MatListModule, MatButtonModule
  ],
  template: `
  <mat-sidenav-container class="layout">
    <mat-sidenav
      #snav
      [mode]="(isHandset$ | async) ? 'over' : 'side'"
      [opened]="!(isHandset$ | async)"
      class="sidenav"
    >
      <mat-toolbar class="sidenav__header">
        <span class="brand">Trip&Share</span>
      </mat-toolbar>

      <mat-nav-list class="nav">
        <a mat-list-item routerLink="/trips" routerLinkActive="active"
           *ngIf="!(isHandset$ | async); else tripsMobile">
          <mat-icon matListItemIcon>receipt_long</mat-icon>
          <span matListItemTitle>Trips</span>
        </a>
        <ng-template #tripsMobile>
          <a mat-list-item routerLink="/trips" routerLinkActive="active" (click)="snav.close()">
            <mat-icon matListItemIcon>receipt_long</mat-icon>
            <span matListItemTitle>Trips</span>
          </a>
        </ng-template>

        <a mat-list-item routerLink="/settings" routerLinkActive="active"
           *ngIf="!(isHandset$ | async); else settingsMobile">
          <mat-icon matListItemIcon>settings</mat-icon>
          <span matListItemTitle>Settings</span>
        </a>
        <ng-template #settingsMobile>
          <a mat-list-item routerLink="/settings" routerLinkActive="active" (click)="snav.close()">
            <mat-icon matListItemIcon>settings</mat-icon>
            <span matListItemTitle>Settings</span>
          </a>
        </ng-template>
      </mat-nav-list>
    </mat-sidenav>

    <mat-sidenav-content>
      <mat-toolbar class="topbar">
        <button mat-icon-button (click)="snav.toggle()" *ngIf="(isHandset$ | async)">
          <mat-icon>menu</mat-icon>
        </button>
        <span class="topbar__title">Trip&Share</span>
        <span class="spacer"></span>
        <button mat-flat-button color="primary">
          <mat-icon>add</mat-icon>
          Add Expense
        </button>
      </mat-toolbar>

      <main class="content">
        <router-outlet></router-outlet>
      </main>
    </mat-sidenav-content>
  </mat-sidenav-container>
  `,
  styles: [`
    /* wysokosc pelnego widoku i brak poziomego scrolla */
    .layout {
      height: 100dvh;
      background: transparent;
      overflow-x: hidden;
      width: 100%;
    }
    .mat-drawer-container, .mat-drawer-content { overflow-x: hidden; }

    /* boczny pasek — bez „szczeliny” (cień do środka) */
    .sidenav {
      width: 272px;
      background: var(--surface);
      color: var(--text);
      box-shadow: inset -1px 0 0 var(--outline);
      height: 100dvh;
    }
    .sidenav__header {
      height: 64px; padding: 0 16px;
      background: transparent; color: var(--text);
    }
    .brand { font-weight: 700; letter-spacing: .3px; }

    .nav a { color: var(--text); }

    /* gorny pasek — lekki blur, bez przerwy z boku */
    .topbar {
      position: sticky; top: 0; z-index: 10;
      height: 64px;
      backdrop-filter: blur(10px);
      background: color-mix(in srgb, var(--surface) 88%, transparent);
      box-shadow: 0 1px 0 var(--outline);
      color: var(--text);
    }
    .topbar, .sidenav__header {
      box-shadow: none;
      border-bottom: 1px solid var(--outline);
    }

    .topbar__title { font-weight: 600; }
    .spacer { flex: 1 1 auto; }

    /* przewijanie tylko tresci */
    .content {
      height: calc(100dvh - 64px);
      overflow: auto;
      padding: 24px;
      max-width: 1120px;
      margin: 0 auto;
      color: var(--text);
    }
  `]
})
export class ShellComponent {
  /* telefon4ik */
  private bp = inject(BreakpointObserver);
  isHandset$ = this.bp.observe([Breakpoints.Handset]).pipe(map(r => r.matches));
}
