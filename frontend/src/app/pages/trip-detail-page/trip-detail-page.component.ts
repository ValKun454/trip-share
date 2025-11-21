import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ApiService } from '../../core/services/api.service';
import { GetTrip } from '../../core/models/trip.model';
import { Expense } from '../../core/models/expense.model';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-trip-detail-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatToolbarModule,
    MatCheckboxModule,
    MatDividerModule,
    MatTooltipModule
  ],
  templateUrl: './trip-detail-page.component.html',
  styleUrls: ['./trip-detail-page.component.css']
})
export class TripDetailPageComponent implements OnInit {
  private api = inject(ApiService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);

  // Trip + gotowa etykieta dat
  trip: (GetTrip & { dates: string }) | null = null;
  expenses: Expense[] = [];
  loading = true;
  error: string | null = null;
  showAddExpense = false;

  currentUser = this.auth.getCurrentUser();

  expenseForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    description: [''],
    totalCost: ['', [Validators.required, Validators.min(0.01)]],
    payerId: [this.currentUser?.id || '', Validators.required],
    isScanned: [false],
    isEvenDivision: [true]
  });

  ngOnInit() {
    const tripId = this.route.snapshot.paramMap.get('id');
    if (tripId) {
      this.loadTripDetails(tripId);
    } else {
      this.error = 'Trip ID not found';
      this.loading = false;
    }
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
   * Wyciąga etykietę dat z opisu tripa.
   * Szuka dat w formacie dd.MM.yyyy w polu description.
   * Jeżeli nic nie znajdzie – używa daty utworzenia.
   */
  private buildDatesLabel(trip: GetTrip): string {
    const desc = trip.description || '';
    const regex = /(\d{2}\.\d{2}\.\d{4})/g;
    const matches = desc.match(regex);

    if (matches && matches.length > 0) {
      const unique = Array.from(new Set(matches));
      if (unique.length === 1) {
        return unique[0];
      }
      if (unique.length >= 2) {
        return `${unique[0]} – ${unique[1]}`;
      }
    }

    return this.formatDateFromIso(trip.createdAt);
  }

  loadTripDetails(tripId: string) {
    this.loading = true;
    this.error = null;

    this.api.getTrip(Number(tripId)).subscribe({
      next: (trip) => {
        this.trip = {
          ...trip,
          dates: this.buildDatesLabel(trip)
        };
        this.loadExpenses(tripId);
      },
      error: (e) => {
        console.error('Failed to load trip', e);
        this.error = e?.error?.detail || 'Failed to load trip';
        this.loading = false;
      }
    });
  }

  loadExpenses(tripId: string) {
    this.api.getExpenses(Number(tripId)).subscribe({
      next: (expenses) => {
        this.expenses = expenses;
        this.loading = false;
      },
      error: (e) => {
        console.error('Failed to load expenses', e);
        this.expenses = [];
        this.loading = false;
      }
    });
  }

  toggleAddExpense() {
    this.showAddExpense = !this.showAddExpense;
    if (!this.showAddExpense) {
      this.expenseForm.reset({
        payerId: this.currentUser?.id,
        isScanned: false,
        isEvenDivision: true
      });
    }
  }

  addExpense() {
    if (!this.expenseForm.valid || !this.trip) {
      this.expenseForm.markAllAsTouched();
      return;
    }

    const tripId = this.trip.id;
    const formValue = this.expenseForm.value;

    const payload = {
      isScanned: formValue.isScanned || false,
      name: formValue.name || '',
      description: formValue.description || '',
      payerId: Number(formValue.payerId) || 0,
      isEvenDivision: formValue.isEvenDivision || true,
      totalCost: Number(formValue.totalCost) || 0
    };

    this.api.createExpense(tripId, payload).subscribe({
      next: () => {
        this.toggleAddExpense();
        this.loadExpenses(String(tripId));
      },
      error: (e) => {
        console.error('Failed to add expense', e);
        this.error = e?.error?.detail || 'Failed to add expense';
      }
    });
  }

  deleteExpense(expenseId: number) {
    if (!confirm('Are you sure you want to delete this expense?')) {
      return;
    }

    if (!this.trip) return;

    // Backend nie ma endpointu delete – tylko komunikat
    alert('Delete functionality not yet implemented on backend');
  }

  editTrip() {
    alert('Edit trip functionality coming soon');
  }

  deleteTrip() {
    if (!this.trip || !confirm('Are you sure you want to delete this trip? This action cannot be undone.')) {
      return;
    }

    this.api.deleteTrip(this.trip.id).subscribe({
      next: () => {
        console.log('Trip deleted successfully');
        this.router.navigate(['/trips']);
      },
      error: (e) => {
        console.error('Delete trip failed', e);
        this.error = e?.error?.detail || 'Failed to delete trip';
      }
    });
  }

  goBack() {
    this.router.navigate(['/trips']);
  }

  formatCurrency(value: unknown): string {
    const num = Number(value) || 0;
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN'
    }).format(num);
  }
}
