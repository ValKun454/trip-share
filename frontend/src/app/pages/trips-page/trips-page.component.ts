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
import { MAT_DATE_FORMATS, MAT_DATE_LOCALE, DateAdapter } from "@angular/material/core";
import { RouterModule } from "@angular/router";
import { ApiService } from "../../core/services/api.service";
import { GetTrip, CreateTrip } from "../../core/models/trip.model";

/**
 * Formatki daty dla polskiego formatu dd.MM.yyyy
 */
const PL_DATE_FORMATS = {
  parse: { dateInput: 'dd.MM.yyyy' },
  display: {
    dateInput: 'dd.MM.yyyy',
    monthYearLabel: 'MMM yyyy',
    dateA11yLabel: 'dd.MM.yyyy',
    monthYearA11yLabel: 'MMMM yyyy'
  }
};

/**
 * Walidator zakresu dat – start <= end
 */
function startBeforeEnd(): ValidatorFn {
  return (group: AbstractControl) => {
    const start = group.get('startDate')?.value as Date | null;
    const end = group.get('endDate')?.value as Date | null;
    // walidujemy tylko jeżeli obie daty są ustawione
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
  // Model wyświetlania: Trip + sformatowane daty (start–end)
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
  // Adapter daty Angular Material – ustawimy mu locale na PL
  private dateAdapter = inject<DateAdapter<Date>>(DateAdapter as any);

  ngOnInit(): void {
    // Ustawiamy lokalizację na pl-PL, żeby input pokazywał dd.MM.yyyy,
    // a nie amerykański format MM/DD/YYYY.
    this.dateAdapter.setLocale('pl-PL');

    this.loadTrips();
  }


  /**
   * Formatuje obiekt Date / string do "dd.MM.yyyy"
   */
  private toDDMMYYYY(d: unknown): string {
    if (!d) return '';
    const date = d instanceof Date ? d : new Date(d as any);
    if (isNaN(date.getTime())) return String(d).trim();
    const dd = String(date.getDate()).padStart(2, '0');
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const yyyy = date.getFullYear();
    return `${dd}.${mm}.${yyyy}`;
  }

  /**
   * Fallback – formatowanie createdAt do "dd.MM.yyyy"
   */
  private formatDateFromIso(isoDateString: string): string {
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

  /**
   * Buduje etykietę dat na karcie tripa.
   * Priorytet:
   *  1) daty wyciągnięte z description (wzór dd.MM.yyyy),
   *  2) w razie braku – data utworzenia (createdAt).
   */
  private buildDatesLabel(trip: GetTrip): string {
    const desc = trip.description || '';
    const regex = /(\d{2}\.\d{2}\.\d{4})/g;
    const matches = desc.match(regex);

    if (matches && matches.length > 0) {
      const unique = Array.from(new Set(matches));
      if (unique.length === 1) {
        return unique[0]; // tylko jedna data
      }
      if (unique.length >= 2) {
        return `${unique[0]} – ${unique[1]}`; // zakres dat
      }
    }

    // jeżeli w opisie nie ma dat – pokaż datę utworzenia
    return this.formatDateFromIso(trip.createdAt);
  }

  loadTrips() {
    this.loading = true;
    this.error = null;
    this.api.getTrips().subscribe({
      next: (list) => {
        // Backend zwraca: id, name, createdAt, creatorId, participants, description
        this.trips = list.map(t => ({
          ...t,
          dates: this.buildDatesLabel(t)
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

  createTrip() {
    // Wymagamy tylko nazwy; daty i uczestnicy są opcjonalni
    const nameControl = this.form.get('name');
    if (!nameControl || !nameControl.valid) {
      this.form.markAllAsTouched();
      console.warn('Form invalid: name is required');
      return;
    }

    const val = this.form.value as any;
    const name = (val.name ?? '').toString().trim();
    const participantsRaw = (val.participants ?? '').toString().trim();

    // Parsujemy uczestników jako ID użytkowników oddzielone przecinkiem
    const participants: number[] = participantsRaw
      ? participantsRaw
          .split(',')
          .map((s: string) => {
            const num = parseInt(s.trim(), 10);
            return isNaN(num) ? 0 : num;
          })
          .filter((num: number) => num > 0)
      : [];

    // daty z formularza -> stringi "dd.MM.yyyy"
    const startLabel = this.toDDMMYYYY(val.startDate);
    const endLabel = this.toDDMMYYYY(val.endDate);

    // opis zapisujemy tak, żeby dało się go później łatwo sparsować
    let description = '';
    if (startLabel && endLabel) {
      description = `Trip: ${startLabel} – ${endLabel}`;
    } else if (startLabel) {
      description = `Trip: ${startLabel}`;
    } else if (endLabel) {
      description = `Trip: do ${endLabel}`;
    } else {
      description = '';
    }

    const dto: CreateTrip = {
      name,
      description,
      participants
    };

    console.log('Creating trip with DTO:', dto);

    this.api.createTrip(dto).subscribe({
      next: (response: any) => {
        console.log('Trip created successfully:', response);
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
