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
  trips: GetTrip[] = [];
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

  loadTrips() {
    this.loading = true;
    this.error = null;
    this.api.getTrips().subscribe({
      next: (list) => {
        // Backend might return with 'id' or needs ID mapping from response
        this.trips = list.map(t => ({
          id: String(t.id || ''),
          name: t.name || '',
          dates: t.dates || '',
          participants: t.participants || []
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

    const start = this.toDDMMYYYY(val.startDate);
    const end = this.toDDMMYYYY(val.endDate);
    let datesStr = '';
    if (start && end) datesStr = `${start} – ${end}`;
    else if (start)   datesStr = start;
    else if (end)     datesStr = end;

    const participantsRaw = (val.participants ?? '').toString();
    const dto: CreateTrip = {
      name,
      dates: datesStr,
      participants: participantsRaw
        ? participantsRaw.split(',').map((s: string) => s.trim()).filter((s: string) => !!s)
        : []
    };

    console.log('Creating trip with DTO:', dto);

    this.api.createTrip(dto).subscribe({
      next: (response: any) => {
        console.log('Trip created successfully:', response);
        // Handle both tripId and id field names from backend response
        const tripId = response?.tripId || response?.id;
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
