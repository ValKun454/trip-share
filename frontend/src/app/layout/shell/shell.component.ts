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
  templateUrl: './shell.component.html',
  styleUrls: ['./shell.component.css']
})
export class ShellComponent {
  /* telefon4ik */
  private bp = inject(BreakpointObserver);
  isHandset$ = this.bp.observe([Breakpoints.Handset]).pipe(map(r => r.matches));
}
