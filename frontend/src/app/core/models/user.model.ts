/**
 * Backend UserResponse model - maps to backend schemas.UserResponse
 * Uses Pydantic aliases: isVerified
 */
export interface UserResponse {
  id: number;
  email: string;
  username?: string | null;
  isVerified: boolean;
}
