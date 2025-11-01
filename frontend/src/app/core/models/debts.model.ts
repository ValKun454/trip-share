
export interface DebtsTripSummary {
  trip: { id: string; name: string }; // minimalny opis wycieczki
  youOwe: Record<string, number>;     // JA → komu jestem winien
  owedToYou: Record<string, number>;  // INNI → ile są mi winni
  totalYouOwe: number;                // suma "you owe"
  totalOwedToYou: number;             // suma "owed to you"
}

// Lista podsumowań po wszystkich tripach
export type DebtsSummary = DebtsTripSummary[];
