export interface DebtsTripSummary {
  trip: { id: string; name: string }; // minimal trip descriptor
  youOwe: Record<string, number>;     // current user -> how much they owe to others
  owedToYou: Record<string, number>;  // others -> how much they owe current user
  totalYouOwe: number;                // sum of "you owe"
  totalOwedToYou: number;             // sum of "owed to you"
}

// List of summaries for all trips
export type DebtsSummary = DebtsTripSummary[];
