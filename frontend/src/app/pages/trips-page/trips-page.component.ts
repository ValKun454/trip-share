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
import { MatNativeDateModule, MAT_DATE_FORMATS, MAT_DATE_LOCALE, DateAdapter } from "@angular/material/core";
import { MatTooltipModule } from "@angular/material/tooltip";
import { RouterModule } from "@angular/router";
import { ApiService } from "../../core/services/api.service";
import { GetTrip, CreateTrip } from "../../core/models/trip.model";
import { AuthService } from "../../core/services/auth.service";

/**
 * Date formats for English calendar, but still dd.MM.yyyy in the input
 */
const EN_DATE_FORMATS = {
  parse: { dateInput: 'dd.MM.yyyy' },
  display: {
    dateInput: 'dd.MM.yyyy',
    monthYearLabel: 'MMM yyyy',
    dateA11yLabel: 'dd.MM.yyyy',
    monthYearA11yLabel: 'MMMM yyyy'
  }
};

/**
 * Date range validator – start <= end
 */
function startBeforeEnd(): ValidatorFn {
  return (group: AbstractControl) => {
    const start = group.get('startDate')?.value as Date | null;
    const end = group.get('endDate')?.value as Date | null;
    // validate only if both dates are set
    if (!start || !end) return null;
    return start.getTime() <= end.getTime() ? null : { rangeInvalid: true };
  };
}

@Component({
  selector: "app-trips-page",
  standalone: true,
  providers: [
    // calendar locale is now English 
    { provide: MAT_DATE_LOCALE, useValue: 'en-GB' },
    { provide: MAT_DATE_FORMATS, useValue: EN_DATE_FORMATS }
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
    MatTooltipModule,
    RouterModule
  ],
  templateUrl: "./trips-page.component.html",
  styleUrls: ["./trips-page.component.css"]
})
export class TripsPageComponent implements OnInit {
  // UI model: Trip + formatted dates label
  trips: Array<GetTrip & { dates: string }> = [];
  loading = false;
  error: string | null = null;
  summaries: Record<string, string> = {};

  showCreate = false;
  editingTripId: number | null = null;

  // friends picker
  friends: Array<{ id: number; label: string }> = [];
  selectedFriendIds: number[] = [];
  friendsLoading = false;
  friendsError: string | null = null;
  showFriendsPicker = false;

  form = inject(FormBuilder).group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    description: ['', [Validators.maxLength(500)]],
    startDate: [''],
    endDate: [''],
    participants: ['']
  }, { validators: startBeforeEnd() });

  private api = inject(ApiService);
  private dateAdapter = inject<DateAdapter<Date>>(DateAdapter as any);
  private auth = inject(AuthService);
  currentUser = this.auth.getCurrentUser();

  ngOnInit(): void {
    // calendar language (month/day names) set to English
    this.dateAdapter.setLocale('en-GB');

    this.loadTrips();
    this.loadFriends();
  }

  /**
   * Format Date / string to "dd.MM.yyyy"
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
   * Fallback – format createdAt to "dd.MM.yyyy"
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
   * Build dates label for trip card.
   * Priority:
   *  1) dates extracted from description (dd.MM.yyyy),
   *  2) otherwise – createdAt date.
   */
  private buildDatesLabel(trip: GetTrip): string {
    const desc = trip.description || '';
    const regex = /(\d{2}\.\d{2}\.\d{4})/g;
    const matches = desc.match(regex);

    if (matches && matches.length > 0) {
      const unique = Array.from(new Set(matches));
      if (unique.length === 1) {
        return unique[0]; // single date
      }
      if (unique.length >= 2) {
        return `${unique[0]} – ${unique[1]}`; // range
      }
    }

    // if no dates in description – show createdAt
    return this.formatDateFromIso(trip.createdAt);
  }

  loadTrips() {
    this.loading = true;
    this.error = null;
    this.api.getTrips().subscribe({
      next: (list) => {
        // Backend returns: id, name, createdAt, creatorId, participants, description
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

  loadFriends() {
    this.friendsLoading = true;
    this.friendsError = null;

    this.api.getFriends().subscribe({
      next: (list: any[]) => {
        const meId = this.currentUser?.id;
        const accepted = (list || []).filter(f => f.isAccepted);

        this.friends = accepted.map(f => {
          let friendId: number;
          if (meId && f.userId1 === meId) {
            friendId = f.userId2;
          } else if (meId && f.userId2 === meId) {
            friendId = f.userId1;
          } else {
            // fallback, если по какой-то причине не совпало
            friendId = f.userId2;
          }
          const label = f.friendUsername || `User #${friendId}`;
          return { id: friendId, label };
        });

        this.friendsLoading = false;
      },
      error: (e) => {
        console.error('Failed to load friends', e);
        this.friendsLoading = false;
        this.friendsError = 'Failed to load friends';
      }
    });
  }

  toggleFriendsPicker() {
    this.showFriendsPicker = !this.showFriendsPicker;
  }

  toggleFriendSelection(friendId: number) {
    if (this.selectedFriendIds.includes(friendId)) {
      this.selectedFriendIds = this.selectedFriendIds.filter(id => id !== friendId);
    } else {
      this.selectedFriendIds = [...this.selectedFriendIds, friendId];
    }
  }

  toggleCreate() {
    this.showCreate = !this.showCreate;
    if (!this.showCreate) {
      this.form.reset();
      this.editingTripId = null;
      this.selectedFriendIds = [];
      this.showFriendsPicker = false;
    }
  }

  createTrip() {
    // Require only name; dates and participants are optional
    const nameControl = this.form.get('name');
    if (!nameControl || !nameControl.valid) {
      this.form.markAllAsTouched();
      console.warn('Form invalid: name is required');
      return;
    }

    const val = this.form.value as any;
    const name = (val.name ?? '').toString().trim();
    const description = (val.description ?? '').toString().trim();
    const participantsRaw = (val.participants ?? '').toString().trim();

    // Parse participants as user IDs, comma-separated
    let participants: number[] = participantsRaw
      ? participantsRaw
          .split(',')
          .map((s: string) => {
            const num = parseInt(s.trim(), 10);
            return isNaN(num) ? 0 : num;
          })
          .filter((num: number) => num > 0)
      : [];

    // добавить выбранных друзей
    if (this.selectedFriendIds.length) {
      const set = new Set<number>(participants);
      this.selectedFriendIds.forEach(id => set.add(id));
      participants = Array.from(set);
    }

    // dates from form -> "dd.MM.yyyy"
    const startLabel = this.toDDMMYYYY(val.startDate);
    const endLabel = this.toDDMMYYYY(val.endDate);

    // description: if user typed, use it; otherwise build from dates
    let finalDescription = description;
    if (!finalDescription) {
      if (startLabel && endLabel) {
        finalDescription = `Trip: ${startLabel} – ${endLabel}`;
      } else if (startLabel) {
        finalDescription = `Trip: ${startLabel}`;
      } else if (endLabel) {
        finalDescription = `Trip: to ${endLabel}`;
      } else {
        finalDescription = '';
      }
    }

    // editing or creating?
    if (this.editingTripId) {
      const updateDto = {
        name,
        description: finalDescription,
        participants
      };
      console.log('Updating trip', this.editingTripId, 'with DTO:', updateDto);
      this.api.updateTrip(this.editingTripId, updateDto).subscribe({
        next: (response: any) => {
          console.log('Trip updated successfully:', response);
          this.toggleCreate();
          this.loadTrips();
        },
        error: (e) => {
          console.error('Update trip failed', e);
          this.error = e?.error?.detail || 'Failed to update trip';
        }
      });
    } else {
      const dto: CreateTrip = {
        name,
        description: finalDescription,
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

  editTrip(trip: GetTrip) {
    this.editingTripId = trip.id;
    this.form.patchValue({
      name: trip.name,
      description: trip.description || '',
      participants: trip.participants?.join(', ') || ''
    });
    this.selectedFriendIds = trip.participants
      ? trip.participants.filter(id => this.friends.some(f => f.id === id))
      : [];
    this.showCreate = true;
    setTimeout(() => {
      document.querySelector('.create-panel')?.scrollIntoView({ behavior: 'smooth' });
    });
  }

  deleteTrip(tripId: number) {
    if (!confirm('Are you sure you want to delete this trip? This action cannot be undone.')) {
      return;
    }

    this.api.deleteTrip(tripId).subscribe({
      next: () => {
        console.log('Trip deleted successfully');
        this.loadTrips();
      },
      error: (e) => {
        console.error('Delete trip failed', e);
        this.error = e?.error?.detail || 'Failed to delete trip';
      }
    });
  }
}
