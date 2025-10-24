export interface GetTrip {
  id: string;
  name: string;
  dates: string;               
  participants: string[];      
}

export interface CreateTrip {
  name: string;
  dates: string;
  participants?: string[];
}