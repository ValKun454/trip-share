import { Component, inject, OnInit } from "@angular/core";
import { CommonModule, NgFor, NgIf } from "@angular/common";
import { ReactiveFormsModule, FormBuilder, Validators } from "@angular/forms";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatInputModule } from "@angular/material/input";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { RouterModule } from "@angular/router";
import { ApiService } from "../../core/services/api.service";
import { GetTrip, CreateTrip } from "../../core/models/trip.model";

@Component({
  selector: "app-trips-page",
  standalone: true,
  imports: [
    CommonModule,
    NgFor,
    NgIf,
    
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatToolbarModule,
    MatFormFieldModule,
    MatDatepickerModule,
    MatNativeDateModule,
    RouterModule
  ],
  templateUrl: "./trips-page.component.html",
  styleUrls: ["./trips-page.component.css"]
})
export class TripsPageComponent implements OnInit {
  trips: GetTrip[] = [];
  loading = false;
  error: string | null = null;
  summaries: Record<string, string> = {};

  showCreate = false;
  form = inject(FormBuilder).group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    dates: [''],
    participants: ['']
  });

  private api = inject(ApiService);

  ngOnInit(): void {
    this.loadTrips();
  }

  loadTrips() {
    this.loading = true;
    this.error = null;
    this.api.getTrips().subscribe({
      next: (list) => {
        this.trips = list;
        // load summaries for each trip (best-effort)
        this.trips.forEach(t => this.loadSummary(String(t.id)));
        this.loading = false;
      },
      error: (e) => {
        console.error('Trips load failed', e);
        this.error = 'Failed to load trips';
        this.loading = false;
      }
    });
  }

  toggleCreate() {
    this.showCreate = !this.showCreate;
    if (!this.showCreate) this.form.reset();
  }

  createTrip() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const val = this.form.value as any || { name: '', dates: '', participants: '' };
    const name = (val.name ?? '').toString().trim();
    
    // Handle date: may be a Date object from datepicker or a string
    let datesStr = '';
    const datesVal = val.dates;
    if (datesVal) {
      if (datesVal instanceof Date) {
        datesStr = datesVal.toISOString().split('T')[0]; // YYYY-MM-DD
      } else {
        datesStr = datesVal.toString().trim();
      }
    }
    
    const participantsRaw = (val.participants ?? '').toString();
    const dto: CreateTrip = {
      name,
      dates: datesStr || '',
      participants: participantsRaw ? participantsRaw.split(',').map((s: string) => s.trim()).filter((s: string) => !!s) : []
    };

    this.api.createTrip(dto).subscribe({
      next: () => {
        this.toggleCreate();
        this.loadTrips();
      },
      error: (e) => {
        console.error('Create trip failed', e);
        this.error = 'Failed to create trip';
      }
    });
  }

  loadSummary(tripId: string) {
    // best-effort: try /api/trips/{id}/summary via ApiService (if implemented)
    if (!this.api.getTripSummary) {
      this.summaries[tripId] = '—';
      return;
    }
    this.api.getTripSummary(tripId).subscribe({
      next: (res) => {
        if (!res) { this.summaries[tripId] = '—'; return; }
        if (typeof res === 'string') this.summaries[tripId] = res;
        else if (res.summary) this.summaries[tripId] = res.summary;
        else if (res.total) this.summaries[tripId] = String(res.total);
        else this.summaries[tripId] = JSON.stringify(res);
      },
      error: () => {
        this.summaries[tripId] = 'N/A';
      }
    });
  }
}
