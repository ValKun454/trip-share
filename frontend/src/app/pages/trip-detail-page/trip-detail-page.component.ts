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
import { forkJoin } from 'rxjs';

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

  // Trip + formatted date label for the header
  trip: (GetTrip & { dates: string }) | null = null;
  expenses: Expense[] = [];
  loading = true;
  error: string | null = null;
  showAddExpense = false;
  editingExpense: Expense | null = null;

  currentUser = this.auth.getCurrentUser();

  // Expense form
  expenseForm = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    description: [''],
    totalCost: ['', [Validators.required, Validators.min(0.01)]],
    payerId: [this.currentUser?.id || '', Validators.required],
    isScanned: [false],
    isEvenDivision: [true]
  });

  // Invite-friends UI state
  inviteForm = this.fb.group({
    // manual user id, optional – user can also just pick from the list
    friendId: ['']
  });

  friendsForInvite: Array<{ id: number; label: string }> = [];
  selectedInviteFriendIds: number[] = [];
  friendsInviteLoading = false;
  friendsInviteError: string | null = null;
  showInvitePanel = false;
  inviteSuccessMessage: string | null = null;
  inviteErrorMessage: string | null = null;

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
   * Fallback – format ISO string to "dd.MM.yyyy"
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
   * Try to extract dates (dd.MM.yyyy) from description;
   * if nothing is found, fall back to createdAt.
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
        this.loadFriendsForInvite();
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

  /**
   * Load friends that can be invited to this trip (accepted friends
   * that are not already in participants list).
   */
  loadFriendsForInvite() {
    if (!this.trip) {
      return;
    }

    this.friendsInviteLoading = true;
    this.friendsInviteError = null;

    this.api.getFriends().subscribe({
      next: (list: any[]) => {
        const meId = this.currentUser?.id;
        const accepted = (list || []).filter(f => f.isAccepted);

        const participantIds = this.trip?.participants || [];

        this.friendsForInvite = accepted
          .map(f => {
            // support both camelCase and snake_case from backend
            const userId1 = f.userId1 ?? f.user_id_1;
            const userId2 = f.userId2 ?? f.user_id_2;

            let friendId: number;
            if (meId && userId1 === meId) {
              friendId = userId2;
            } else if (meId && userId2 === meId) {
              friendId = userId1;
            } else {
              friendId = userId2 ?? userId1;
            }

            const label = f.friendUsername || f.username || `User #${friendId}`;
            return { id: friendId, label };
          })
          // do not show users who are already participants
          .filter(f => !participantIds.includes(f.id));

        this.friendsInviteLoading = false;
      },
      error: (e) => {
        console.error('Failed to load friends for invites', e);
        this.friendsInviteLoading = false;
        this.friendsInviteError = 'Failed to load friends list';
      }
    });
  }

  toggleInvitePanel() {
    this.showInvitePanel = !this.showInvitePanel;
  }

  toggleInviteFriend(friendId: number) {
    if (this.selectedInviteFriendIds.includes(friendId)) {
      this.selectedInviteFriendIds = this.selectedInviteFriendIds.filter(id => id !== friendId);
    } else {
      this.selectedInviteFriendIds = [...this.selectedInviteFriendIds, friendId];
    }
  }

  /**
   * Send invites based on:
   *  - selected friends from the list
   *  - optional manually typed Friend ID
   */
  sendInvites() {
    if (!this.trip) return;

    this.inviteErrorMessage = null;
    this.inviteSuccessMessage = null;

    const ids = new Set<number>(this.selectedInviteFriendIds);

    const raw = this.inviteForm.get('friendId')?.value;
    if (raw !== null && raw !== undefined && raw !== '') {
      const parsed = Number(raw);
      if (isNaN(parsed) || parsed <= 0) {
        this.inviteErrorMessage = 'Friend ID must be a positive number.';
        return;
      }
      ids.add(parsed);
    }

    if (!ids.size) {
      this.inviteErrorMessage = 'Select at least one friend or enter a Friend ID.';
      return;
    }

    const participantIds = this.trip.participants || [];
    const finalIds = Array.from(ids).filter(id => !participantIds.includes(id));

    if (!finalIds.length) {
      this.inviteErrorMessage = 'All selected users are already participants of this trip.';
      return;
    }

    const requests = finalIds.map(userId =>
      this.api.inviteUserToTrip(this.trip!.id, userId)
    );

    forkJoin(requests).subscribe({
      next: () => {
        this.inviteSuccessMessage = 'Invitations have been sent.';
        this.inviteForm.reset();
        this.selectedInviteFriendIds = [];
        // reload trip to refresh participants counter
        this.loadTripDetails(String(this.trip!.id));
      },
      error: (e) => {
        console.error('Failed to send invites', e);
        const detail = e?.error?.detail;
        this.inviteErrorMessage =
          typeof detail === 'string'
            ? detail
            : 'Failed to send one or more invites.';
      }
    });
  }

  toggleAddExpense() {
    this.showAddExpense = !this.showAddExpense;
    this.editingExpense = null; // Clear editing mode
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

  editExpense(expense: Expense) {
    this.editingExpense = expense;
    this.showAddExpense = true;
    
    // Pre-populate form with expense data
    this.expenseForm.patchValue({
      name: expense.name,
      description: expense.description || '',
      totalCost: String(expense.totalCost),
      payerId: expense.payerId,
      isScanned: expense.isScanned,
      isEvenDivision: expense.isEvenDivision
    });
  }

  saveExpense() {
    if (!this.expenseForm.valid || !this.trip || !this.editingExpense) {
      this.expenseForm.markAllAsTouched();
      return;
    }

    const tripId = this.trip.id;
    const expenseId = this.editingExpense.id;
    const formValue = this.expenseForm.value;

    const payload = {
      isScanned: formValue.isScanned || false,
      name: formValue.name || '',
      description: formValue.description || '',
      payerId: Number(formValue.payerId) || 0,
      isEvenDivision: formValue.isEvenDivision || true,
      totalCost: Number(formValue.totalCost) || 0
    };

    this.api.updateExpense(tripId, expenseId, payload).subscribe({
      next: () => {
        this.editingExpense = null;
        this.toggleAddExpense();
        this.loadExpenses(String(tripId));
      },
      error: (e) => {
        console.error('Failed to update expense', e);
        this.error = e?.error?.detail || 'Failed to update expense';
      }
    });
  }

  deleteExpense(expenseId: number) {
    if (!confirm('Are you sure you want to delete this expense?')) {
      return;
    }

    if (!this.trip) return;

    this.api.deleteExpense(this.trip.id, expenseId).subscribe({
      next: () => {
        console.log('Expense deleted successfully');
        this.loadExpenses(String(this.trip!.id));
      },
      error: (e) => {
        console.error('Delete expense failed', e);
        this.error = e?.error?.detail || 'Failed to delete expense';
      }
    });
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
