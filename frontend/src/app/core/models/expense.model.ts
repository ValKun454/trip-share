export interface Expense {
  id: string;
  tripId: string;
  title: string;
  amount: number;              // raksy
  paidBy: string;              // user id/name
  included: string[];          // skolko?
  date: string;                // nu eto data
}
