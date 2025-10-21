import { Component, inject } from "@angular/core";
import { NgFor } from "@angular/common";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { ApiService, Trip } from "../../core/api.service";

@Component({
  selector: "app-trips-page",
  standalone: true,
  imports: [NgFor, MatCardModule, MatButtonModule],
  template: `
    <section class="header">
      <h2>Your trips</h2>
      <div class="actions">
        <button mat-raised-button color="primary" (click)="loadTrips()">Load from API</button>
        <button mat-stroked-button color="primary">New Trip</button>
      </div>
    </section>

    <div class="grid">
      <mat-card *ngFor="let t of trips" class="trip">
        <mat-card-header>
          <div mat-card-avatar class="avatar">??</div>
          <mat-card-title>{{ t.name }}</mat-card-title>
          <mat-card-subtitle>{{ t.dates }}</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          Participants: {{ t.participants.length }}
        </mat-card-content>
        <mat-card-actions align="end">
          <button mat-button color="primary">Open</button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .header { display:flex; align-items:center; gap:12px; justify-content:space-between; margin-bottom:16px; }
    .actions { display:flex; gap:8px; }
    .grid { display:grid; grid-template-columns: repeat(auto-fill,minmax(260px,1fr)); gap:16px; margin-top:8px; }
    .trip { min-height: 140px; background: var(--surface-high); }
    .avatar {
      width: 40px; height: 40px; display:grid; place-items:center;
      border-radius: 50%;
      background: color-mix(in srgb, var(--primary) 18%, transparent);
    }
  `]
})
export class TripsPageComponent {
  trips: Trip[] = [
    { id: "tmp1", name: "Madeira weekend", dates: "12-14 Apr", participants: ["M"] },
  ];

  private api = inject(ApiService);

  loadTrips() {
    this.api.getTrips().subscribe({
      next: (list) => this.trips = list,
      error: (e) => console.error("Trips load failed", e)
    });
  }
}
