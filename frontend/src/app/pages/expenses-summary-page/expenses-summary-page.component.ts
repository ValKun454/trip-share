import { Component, inject } from '@angular/core';
import { NgFor, NgIf, CurrencyPipe, NgClass } from '@angular/common';
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
    NgClass,
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
  selectedTrip: DebtsTripSummary | null = null;

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

          if (this.selectedTrip) {
            const stillExists = summary.find(
              (s) => s.trip.id === this.selectedTrip!.trip.id,
            );
            if (!stillExists) {
              this.selectedTrip = null;
            }
          }
        },
        error: () => {
          this.data = [];
          this.loading = false;
          this.selectedTrip = null;
        },
      });
  }

  selectTrip(trip: DebtsTripSummary) {
    this.selectedTrip = trip;
  }

  backToSummary() {
    this.selectedTrip = null;
  }

  private buildSummaryForTrip(
    trip: GetTrip,
    oweSummary: TripOweSummary,
  ): DebtsTripSummary {
    const youOwe: DebtsTripSummary['youOwe'] = [];
    const owedToYou: DebtsTripSummary['owedToYou'] = [];

    let totalYouOwe = 0;
    let totalOwedToYou = 0;

    for (const entry of oweSummary.iOweTo) {
      const amount = parseFloat(entry.amount);
      if (!amount || amount <= 0) continue;

      youOwe.push({
        userId: entry.userId,
        userName: entry.userName ?? `User ${entry.userId}`,
        amount,
      });

      totalYouOwe += amount;
    }

    for (const entry of oweSummary.oweToMe) {
      const amount = parseFloat(entry.amount);
      if (!amount || amount <= 0) continue;

      owedToYou.push({
        userId: entry.userId,
        userName: entry.userName ?? `User ${entry.userId}`,
        amount,
      });

      totalOwedToYou += amount;
    }

    return {
      trip: {
        id: trip.id.toString(),
        name: trip.name,
        // For UX: show hint when there's only one participant
        participantsCount: Array.isArray(trip.participants)
          ? trip.participants.length
          : 0,
      },
      youOwe,
      owedToYou,
      totalYouOwe,
      totalOwedToYou,
    };
  }
}
