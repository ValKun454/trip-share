import { Component, inject } from '@angular/core';
import { NgFor, NgIf, KeyValuePipe, CurrencyPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';

import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

import { DebtsSummary, DebtsTripSummary } from '../../core/models/debts.model';
import { GetTrip } from '../../core/models/trip.model';
import { Expense } from '../../core/models/expense.model';

import { forkJoin, of, switchMap, map } from 'rxjs';

@Component({
  selector: 'app-expenses-summary-page',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    KeyValuePipe,
    CurrencyPipe,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatDividerModule,
  ],
  templateUrl: './expenses-summary-page.component.html',
  styleUrls: ['./expenses-summary-page.component.css'],
})
export class ExpensesSummaryPageComponent {
  private api = inject(ApiService);
  private auth = inject(AuthService);

  loading = true;
  data: DebtsSummary = [];

  // userId -> display name (nickname); filled from current user + friends
  private userNames: Record<number, string> = {};

  ngOnInit(): void {
    const user = this.auth.getCurrentUser();
    const currentUserId = user?.id;

    if (!currentUserId) {
      this.data = [];
      this.loading = false;
      return;
    }

    if (user?.username) {
      this.userNames[currentUserId] = user.username;
    }

    // First, best-effort load friends to map userId -> nickname
    this.api.getFriends().subscribe({
      next: (friends: any[]) => {
        this.buildUserNameMapFromFriends(friends, currentUserId);
        this.loadSummary(currentUserId);
      },
      error: () => {
        // If friends endpoint fails, still show summary using IDs only
        this.loadSummary(currentUserId);
      },
    });
  }

  private loadSummary(currentUserId: number): void {
    this.loading = true;

    this.api
      .getTrips()
      .pipe(
        switchMap((trips: GetTrip[]) => {
          if (!trips.length) {
            return of<DebtsSummary>([]);
          }

          const perTrip$ = trips.map((trip) =>
            this.api.getExpenses(trip.id).pipe(
              map((expenses) =>
                this.buildSummaryForTrip(trip, expenses, currentUserId),
              ),
            ),
          );

          return forkJoin(perTrip$);
        }),
      )
      .subscribe({
        next: (summary) => {
          this.data = summary;
          this.loading = false;
        },
        error: () => {
          this.data = [];
          this.loading = false;
        },
      });
  }

  private buildUserNameMapFromFriends(list: any[], currentUserId: number): void {
    const accepted = (list || []).filter((f) => f.isAccepted);

    accepted.forEach((f) => {
      const userId1 = f.userId1 ?? f.user_id_1;
      const userId2 = f.userId2 ?? f.user_id_2;

      let friendId: number;
      if (currentUserId && userId1 === currentUserId) {
        friendId = userId2;
      } else if (currentUserId && userId2 === currentUserId) {
        friendId = userId1;
      } else {
        friendId = userId2 ?? userId1;
      }

      const label = f.friendUsername || f.username || `User ${friendId}`;
      if (typeof friendId === 'number' && label) {
        this.userNames[friendId] = label;
      }
    });
  }

  /**
   * Build DebtsTripSummary for a single trip.
   */
  private buildSummaryForTrip(
    trip: GetTrip,
    expenses: Expense[],
    currentUserId: number,
  ): DebtsTripSummary {
    const participants = trip.participants ?? [];
    const creatorId = trip.creatorId;

    const participantsSet = new Set<number>(participants);
    if (creatorId != null) {
      participantsSet.add(creatorId);
    }
    const tripParticipantIds = Array.from(participantsSet);

    let totalYouOwe = 0;
    let totalOwedToYou = 0;
    const youOwe: Record<string, number> = {};
    const owedToYou: Record<string, number> = {};

    for (const expense of expenses) {
      const payerId = expense.payerId;
      const rawTotal = expense.totalCost;
      const total =
        typeof rawTotal === 'string' ? parseFloat(rawTotal) : rawTotal;

      if (!total || total <= 0) continue;

      const expenseParticipants =
        expense.positions && expense.positions.length
          ? expense.positions
          : tripParticipantIds;

      if (!expenseParticipants || !expenseParticipants.length) continue;

      const share = total / expenseParticipants.length;

      for (const pid of expenseParticipants) {
        if (pid === payerId) continue;

        // current user owes money to payer
        if (pid === currentUserId && payerId !== currentUserId) {
          const key = this.formatUserKey(payerId);
          youOwe[key] = (youOwe[key] ?? 0) + share;
          totalYouOwe += share;
        }

        // someone owes money to current user
        if (payerId === currentUserId && pid !== currentUserId) {
          const key = this.formatUserKey(pid);
          owedToYou[key] = (owedToYou[key] ?? 0) + share;
          totalOwedToYou += share;
        }
      }
    }

    const summary: DebtsTripSummary = {
      trip: {
        id: trip.id.toString(),
        name: trip.name,
      },
      youOwe,
      owedToYou,
      totalYouOwe,
      totalOwedToYou,
    };

    return summary;
  }

  /**
   * Key format used in youOwe / owedToYou maps:
   * "<displayName>|<userId>".
   */
  private formatUserKey(userId: number): string {
    const name = this.userNames[userId] ?? `User ${userId}`;
    return `${name}|${userId}`;
  }

  // --- helpers used in the template (for name + ID chip) ---

  getDisplayName(key: string): string {
    const [name] = key.split('|');
    return name || key;
  }

  getUserIdFromKey(key: string): string {
    const parts = key.split('|');
    return parts[1] ?? '';
  }
}
