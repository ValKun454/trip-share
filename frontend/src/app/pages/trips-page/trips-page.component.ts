import { Component, inject, OnInit } from "@angular/core";
import { CommonModule, NgFor, NgIf } from "@angular/common";
import { ReactiveFormsModule, FormBuilder, Validators, ValidatorFn, AbstractControl } from "@angular/forms";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatInputModule } from "@angular/material/input";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatDatepickerModule } from "@angular/material/datepicker";
import { MatNativeDateModule } from "@angular/material/core";
import { MAT_DATE_FORMATS, MAT_DATE_LOCALE } from "@angular/material/core";
import { RouterModule } from "@angular/router";
import { ApiService } from "../../core/services/api.service";
import { GetTrip, CreateTrip } from "../../core/models/trip.model";

const PL_DATE_FORMATS = {
  parse: { dateInput: 'DD.MM.YYYY' },
  display: {
    dateInput: 'DD.MM.YYYY',
    monthYearLabel: 'MMM YYYY',
    dateA11yLabel: 'DD.MM.YYYY',
    monthYearA11yLabel: 'MMMM YYYY'
  }
};

function startBeforeEnd(): ValidatorFn {
  return (group: AbstractControl) => {
    const start = group.get('startDate')?.value as Date | null;
    const end = group.get('endDate')?.value as Date | null;
    // Only validate if both dates are present
    if (!start || !end) return null;
    return start.getTime() <= end.getTime() ? null : { rangeInvalid: true };
  };
}

@Component({
  selector: "app-trips-page",
  standalone: true,
  providers: [
    { provide: MAT_DATE_LOCALE, useValue: 'pl-PL' },
    { provide: MAT_DATE_FORMATS, useValue: PL_DATE_FORMATS }
  ],
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
  // Display model: extends GetTrip with formatted dates string for UI
  trips: Array<GetTrip & { dates: string }> = [];
  loading = false;
  error: string | null = null;
  summaries: Record<string, string> = {};

  showCreate = false;

  form = inject(FormBuilder).group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    startDate: [''],
    endDate: [''],
    participants: ['']
  }, { validators: startBeforeEnd() });

  private api = inject(ApiService);

  ngOnInit(): void {
    this.loadTrips();
  }

  /** Format ISO date string to DD.MM.YYYY format for display */
  private formatDates(isoDateString: string): string {
    try {
      const date = new Date(isoDateString);
      if (isNaN(date.getTime())) return '—';
      const dd = String(date.getDate()).padStart(2, '0');
      const mm = String(date.getMonth() + 1).padStart(2, '0');
      const yyyy = date.getFullYear();
      return `${dd}.${mm}.${yyyy}`;
    } catch {
      return '—';
    }
  }

  loadTrips() {
    this.loading = true;
    this.error = null;
    this.api.getTrips().subscribe({
      next: (list) => {
        // Backend returns trips with id, name, createdAt, creatorId, participants, description
        this.trips = list.map(t => ({
          ...t,
          dates: this.formatDates(t.createdAt) // Add formatted dates for display
        }));
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

  private toDDMMYYYY(d: unknown): string {
    if (!d) return '';
    const date = d instanceof Date ? d : new Date(d as any);
    if (isNaN(date.getTime())) return String(d).trim();
    const dd = String(date.getDate()).padStart(2, '0');
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const yy = date.getFullYear();
    return `${dd}.${mm}.${yy}`;
  }

  createTrip() {
    // Only require name field to be valid; dates and participants are optional
    const nameControl = this.form.get('name');
    if (!nameControl || !nameControl.valid) {
      this.form.markAllAsTouched();
      console.warn('Form invalid: name is required');
      return;
    }

    const val = this.form.value as any;
    const name = (val.name ?? '').toString().trim();
    const participantsRaw = (val.participants ?? '').toString().trim();

    // Parse participants as comma-separated user IDs (convert to numbers)
    const participants: number[] = participantsRaw
      ? participantsRaw.split(',').map((s: string) => {
        const num = parseInt(s.trim(), 10);
        return isNaN(num) ? 0 : num;
      }).filter((num: number) => num > 0)
      : [];

    // Create trip DTO - backend expects { name, description, participants }
    const dto: CreateTrip = {
      name,
      description: `Trip from ${new Date().toLocaleDateString()}`, // Auto-generate simple description
      participants
    };

    console.log('Creating trip with DTO:', dto);

    this.api.createTrip(dto).subscribe({
      next: (response: any) => {
        console.log('Trip created successfully:', response);
        // Backend returns full Trip object with id field
        const tripId = response?.id;
        if (tripId) {
          this.toggleCreate();
          this.loadTrips();
        } else {
          this.error = 'Trip created but response format unexpected';
        }
      },
      error: (e) => {
        console.error('Create trip failed', e);
        this.error = e?.error?.detail || 'Failed to create trip';
      }
    });
  }

  loadSummary(tripId: string) {
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
