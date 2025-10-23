import { Component, inject } from "@angular/core";
import { NgFor } from "@angular/common";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { ApiService} from "../../core/services/api.service";
import { GetTrip } from "../../core/models/trip.model";


@Component({
  selector: "app-trips-page",
  standalone: true,
  imports: [NgFor, MatCardModule, MatButtonModule],
  templateUrl: "./trips-page.component.html",
  styleUrls: ["./trips-page.component.css"]
})
export class TripsPageComponent {
  trips: GetTrip[] = [
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
