// Podsumowanie pojedynczej wycieczki na ekranie "Total expenses".

export interface DebtsPersonRow {
  userId: number;
  userName: string;
  amount: number;
}

export interface DebtsTripSummary {
  // We keep minimal trip info, plus optional participantsCount for UX hints
  trip: { id: string; name: string; participantsCount?: number };
  // kogo JA jestem winien
  youOwe: DebtsPersonRow[];
  // kto jest winien MNIE
  owedToYou: DebtsPersonRow[];
  totalYouOwe: number;
  totalOwedToYou: number;
}

// Lista podsumowań po wszystkich tripach
export type DebtsSummary = DebtsTripSummary[];
export interface TripOweEntry {
  userId: number;
  userName: string | null;
  amount: string;
}

export interface TripOweSummary {
  // oni są mi winni
  oweToMe: TripOweEntry[];
  // ja jestem winien innym
  iOweTo: TripOweEntry[];
}
