// Prosty model odpowiedzi TripInvite z backendu
export interface TripInvite {
  id: number;
  tripId: number;
  inviteeId: number;
  inviterId: number;
  status: string; // "pending" / "accepted" / "declined"
  createdAt: string;
  tripName?: string | null;
  inviteeUsername?: string | null;
  inviterUsername?: string | null;
}
