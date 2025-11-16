/**
 * Backend Expense response model - maps to backend schemas.Expense
 * Uses Pydantic aliases: isScanned, createdAt, tripId, payerId, isEvenDivision
 */
export interface Expense {
  id: number;
  isScanned: boolean;
  name: string; // Not 'title'
  description?: string | null;
  createdAt: string; // ISO format datetime
  tripId: number;
  payerId: number; // User ID, not name/string
  isEvenDivision: boolean;
  totalCost: number | string; // Decimal from backend (handle as string or number)
  positions: number[]; // List of user IDs who are included in this expense
}

/**
 * DTO for creating an expense - only the fields needed to send to backend
 */
export interface ExpenseCreate {
  isScanned: boolean;
  name: string;
  description?: string;
  payerId: number;
  isEvenDivision: boolean;
  totalCost: number | string;
}
