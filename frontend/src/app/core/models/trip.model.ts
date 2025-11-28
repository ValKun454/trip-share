/**
 * Backend Trip response model - maps to backend schemas.Trip
 * Uses Pydantic aliases: createdAt (created_at), creatorId (creator_id)
 */
export interface GetTrip {
  id: number;
  name: string;
  description?: string | null;
  createdAt: string; // ISO format datetime from backend
  creatorId: number;
  participants: number[]; // List of user IDs (not strings)
}

/**
 * Create trip DTO - backend expects { name, description, participants }
 * Participants should be user IDs (numbers), not names
 */
export interface CreateTrip {
  name: string;
  description?: string;
  participants?: number[]; // User ID
}