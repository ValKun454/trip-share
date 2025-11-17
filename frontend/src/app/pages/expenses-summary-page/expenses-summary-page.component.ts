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

  ngOnInit() {
    const user = this.auth.getCurrentUser();
    const currentUserId = user?.id;

    if (!currentUserId) {
      this.data = [];
      this.loading = false;
      return;
    }

    this.api
      .getTrips()
      .pipe(
        // dla każdego tripu
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

          // czekamy dopóki każdy request zostanie opracowany
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

  /**
  * Obliczamy DebtsTripSummary dla pojedynczej podróży.
  * Logika:
  * - jeśli wydatek ma pozycje → podziel kwotę tylko między nimi;
  * - jeśli pozycje są puste → podziel kwotę między wszystkimi uczestnikami podróży
  * (trip.participants + creatorId).
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

    // tymczsowy nickname dopoki nie mamy id
    const getName = (userId: number) => `User ${userId}`;

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
        if (pid === payerId) continue; // nie winien sam sobie

        // user winien
        if (pid === currentUserId && payerId !== currentUserId) {
          const creditorName = getName(payerId);
          youOwe[creditorName] = (youOwe[creditorName] ?? 0) + share;
          totalYouOwe += share;
        }

        // ktoś winien
        if (payerId === currentUserId && pid !== currentUserId) {
          const debtorName = getName(pid);
          owedToYou[debtorName] = (owedToYou[debtorName] ?? 0) + share;
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
}
