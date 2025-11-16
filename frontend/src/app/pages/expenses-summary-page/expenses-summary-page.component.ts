import { Component, inject } from '@angular/core';
import { NgFor, NgIf, KeyValuePipe, CurrencyPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';

import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';
import { DebtsSummary } from '../../core/models/debts.model';

@Component({
  selector: 'app-expenses-summary-page',
  standalone: true,
  imports: [NgFor, NgIf, KeyValuePipe, CurrencyPipe, MatCardModule, MatChipsModule, MatIconModule, MatDividerModule],
  templateUrl: './expenses-summary-page.component.html',
  styleUrls: ['./expenses-summary-page.component.css']
})
export class ExpensesSummaryPageComponent {
  private api = inject(ApiService);
  private auth = inject(AuthService);

  loading = true;
  data: DebtsSummary = [];

  ngOnInit() {
    const user = this.auth.getCurrentUser();
    // Backend doesn't have /debts/summary endpoint yet
    // Load all trips and build summary from expenses data
    if (user?.id) {
      this.api.getTrips().subscribe({
        next: (trips) => {
          // TODO: Calculate debts from trips + expenses when backend provides full data
          this.data = [];
          this.loading = false;
        },
        error: () => {
          this.data = [];
          this.loading = false;
        }
      });
    } else {
      this.data = [];
      this.loading = false;
    }
  }
}
