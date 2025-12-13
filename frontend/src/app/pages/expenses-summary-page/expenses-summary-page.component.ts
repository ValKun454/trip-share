// frontend/src/app/pages/expenses-summary-page/expenses-summary-page.component.ts

import { Component, inject } from '@angular/core';
import { NgFor, NgIf, KeyValuePipe, CurrencyPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';

import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

import {
  DebtsSummary,
  DebtsTripSummary,
  TripOweSummary,
} from '../../core/models/debts.model';
import { GetTrip } from '../../core/models/trip.model';

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
        switchMap((trips: GetTrip[]) => {
          if (!trips.length) {
            return of<DebtsSummary>([]);
          }

          const perTrip$ = trips.map((trip) =>
            this.api.getTripOweSummary(trip.id).pipe(
              map((oweSummary: TripOweSummary) =>
                this.buildSummaryForTrip(trip, oweSummary),
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

  /**
   * Build DebtsTripSummary for a single trip based on /trips/{id}/owe response.
   *
   * Backend JSON (camelCase):
   * {
   *   oweToMe: [{ userId, userName, amount }],
   *   iOweTo:  [{ userId, userName, amount }]
   * }
   */
  private buildSummaryForTrip(
    trip: GetTrip,
    rawOwe: TripOweSummary,
  ): DebtsTripSummary {
    const parseAmount = (raw: string): number => {
      const v = parseFloat(raw);
      return Number.isNaN(v) ? 0 : v;
    };

    const oweToMeRaw = rawOwe?.oweToMe ?? [];
    const iOweToRaw = rawOwe?.iOweTo ?? [];

    const owedToYou = oweToMeRaw
      .map((item) => ({
        userId: item.userId,
        userName: item.userName ?? `User ${item.userId}`,
        amount: parseAmount(item.amount),
      }))
      .filter((x) => x.amount > 0);

    const youOwe = iOweToRaw
      .map((item) => ({
        userId: item.userId,
        userName: item.userName ?? `User ${item.userId}`,
        amount: parseAmount(item.amount),
      }))
      .filter((x) => x.amount > 0);

    const totalYouOwe = youOwe.reduce((sum, x) => sum + x.amount, 0);
    const totalOwedToYou = owedToYou.reduce((sum, x) => sum + x.amount, 0);

    return {
      trip: {
        id: trip.id.toString(),
        name: trip.name,
      },
      youOwe,
      owedToYou,
      totalYouOwe,
      totalOwedToYou,
    };
  }
}
