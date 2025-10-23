import { Component, inject } from "@angular/core";
import { RouterOutlet, RouterLink, RouterLinkActive } from "@angular/router";
import { BreakpointObserver, Breakpoints } from "@angular/cdk/layout";
import { map } from "rxjs";
import { NgIf, AsyncPipe, DatePipe } from "@angular/common";

import { MatSidenavModule } from "@angular/material/sidenav";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";
import { MatListModule } from "@angular/material/list";
import { MatButtonModule } from "@angular/material/button";
import { MatMenuModule } from "@angular/material/menu";
import { MatDividerModule } from "@angular/material/divider";
import { AuthService } from "../../core/services/auth.service";

@Component({
  selector: "app-root",
  standalone: true,
  imports: [
    RouterOutlet, RouterLink, RouterLinkActive, NgIf, AsyncPipe, DatePipe,
    MatSidenavModule, MatToolbarModule, MatIconModule, MatListModule, 
    MatButtonModule, MatMenuModule, MatDividerModule
  ],
  templateUrl: './shell.component.html',
  styleUrls: ['./shell.component.css']
})
export class ShellComponent {
  /* telefon4ik */
  private bp = inject(BreakpointObserver);
  private authService = inject(AuthService);
  
  isHandset$ = this.bp.observe([Breakpoints.Handset]).pipe(map(r => r.matches));
  isLoggedIn$ = this.authService.isLoggedIn$;

  logout() {
    this.authService.logout();
  }

  getCurrentUser() {
    return this.authService.getCurrentUser();
  }
}
