import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  AbstractControl,
  ValidationErrors
} from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { ApiService } from '../../core/services/api.service';
import { TripInvite } from '../../core/models/trip-invite.model';

interface Friend {
  id?: number;
  userId1?: number;
  userId2?: number;
  user_id_1?: number;  // fallback for snake_case
  user_id_2?: number;  // fallback for snake_case
  username?: string;
  email?: string;
  created_at?: string;
  isAccepted?: boolean;
  friendUsername?: string;
}

interface CurrentUser {
  id: number;
  email: string;
  username: string;
  isVerified: boolean;
}

// Custom validator: positive integer in a text field
function positiveIntegerValidator(control: AbstractControl): ValidationErrors | null {
  if (!control.value) {
    return null; // "required" handled separately
  }
  const value = Number(control.value);
  if (isNaN(value) || value <= 0 || !Number.isInteger(value)) {
    return { positiveInteger: true };
  }
  return null;
}

@Component({
  selector: 'app-friends-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatToolbarModule
  ],
  templateUrl: './friends-page.component.html',
  styleUrls: ['./friends-page.component.css']
})
export class FriendsPageComponent implements OnInit {
  private api = inject(ApiService);
  private fb = inject(FormBuilder);

  friends: Friend[] = [];
  friendRequests: Friend[] = [];
  loading = false;
  error: string | null = null;
  successMessage: string | null = null;
  currentUser: CurrentUser | null = null;

  addFriendForm: FormGroup;

  // Trip invites section
  tripInvites: TripInvite[] = [];
  loadingTripInvites = false;

  constructor() {
    this.addFriendForm = this.fb.group({
      userId: ['', [Validators.required, positiveIntegerValidator]]
    });
  }

  ngOnInit(): void {
    // First load the current user so we know their ID
    this.api.getMe().subscribe({
      next: (user) => {
        this.currentUser = user;
        this.loadFriends();
        this.loadFriendRequests();
        this.loadTripInvites();
      },
      error: (e) => {
        console.error('Failed to get current user', e);
        this.error = 'Failed to load user info';
      }
    });
  }

  // ---------- FRIENDS ----------

  // Load accepted friends list
  loadFriends(): void {
    this.loading = true;
    this.error = null;

    this.api.getFriends().subscribe({
      next: (friends) => {
        this.friends = (friends || []).filter((f: any) => f.isAccepted);
        this.loading = false;
      },
      error: (e) => {
        console.error('Failed to load friends', e);
        this.error = 'Failed to load friends';
        this.loading = false;
      }
    });
  }

  // Load incoming friend requests
  loadFriendRequests(): void {
    this.api.getFriendRequests().subscribe({
      next: (requests) => {
        this.friendRequests = requests || [];
      },
      error: (e) => {
        console.error('Failed to load friend requests', e);
      }
    });
  }

  // Send a friend request by user ID
  addFriend(): void {
    if (this.addFriendForm.invalid) {
      this.addFriendForm.markAllAsTouched();
      return;
    }

    const friendId = Number(this.addFriendForm.get('userId')?.value);

    // Check if we already have this friend
    if (this.friends.some(f =>
      (f.userId1 === friendId || f.userId2 === friendId) ||
      (f.user_id_1 === friendId || f.user_id_2 === friendId)
    )) {
      this.error = 'This friend is already in your list';
      this.successMessage = null;
      return;
    }

    this.api.addFriend(friendId).subscribe({
      next: () => {
        this.successMessage = `Friend request sent to user ${friendId}`;
        this.error = null;
        this.addFriendForm.reset();
        this.loadFriendRequests();

        setTimeout(() => {
          this.successMessage = null;
        }, 3000);
      },
      error: (e) => {
        console.error('Failed to add friend', e);
        let errorMsg = 'Failed to add friend';

        // Handle validation errors from FastAPI / Pydantic
        if (Array.isArray(e?.error?.detail)) {
          const firstError = e.error.detail[0];
          if (firstError?.msg) {
            errorMsg = firstError.msg;
          } else if (firstError?.type) {
            errorMsg = firstError.type;
          }
        } else if (typeof e?.error?.detail === 'string') {
          errorMsg = e.error.detail;
        } else if (e?.error?.message) {
          errorMsg = e.error.message;
        } else if (e?.message) {
          errorMsg = e.message;
        }
        this.error = errorMsg;
        this.successMessage = null;
      }
    });
  }

  // Accept a friend request
  acceptFriendRequest(request: Friend): void {
    if (!request.id) {
      this.error = 'Error: Missing request id';
      return;
    }

    this.api.acceptFriendRequest(request.id).subscribe({
      next: () => {
        this.successMessage = 'Friend request accepted';
        this.error = null;
        this.loadFriends();
        this.loadFriendRequests();
        setTimeout(() => {
          this.successMessage = null;
        }, 3000);
      },
      error: (e) => {
        console.error('Failed to accept friend request', e);
        let msg = e?.error?.detail || 'Failed to accept friend request';
        if (typeof msg === 'string' && msg.includes('own friend request')) {
          msg = 'This is your outgoing request. The other user has to accept it.';
        }
        this.error = msg;
        this.successMessage = null;
      }
    });
  }

  // Decline a friend request
  declineFriendRequest(request: Friend): void {
    const friendId = this.getOtherFriendId(request);
    if (friendId === 0) {
      this.error = 'Error: Could not determine friend ID';
      return;
    }

    if (!confirm('Decline this friend request?')) {
      return;
    }

    this.api.removeFriend(friendId).subscribe({
      next: () => {
        this.friendRequests = this.friendRequests.filter(r => r.id !== request.id);
        this.successMessage = 'Friend request declined';
        this.error = null;
        setTimeout(() => {
          this.successMessage = null;
        }, 2000);
      },
      error: (e) => {
        console.error('Failed to decline friend request', e);
        this.error = e?.error?.detail || 'Failed to decline friend request';
        this.successMessage = null;
      }
    });
  }

  // Remove an existing friend
  removeFriend(friend: Friend): void {
    let friendId = this.getOtherFriendId(friend);

    if (friendId === 0) {
      friendId = (friend.userId1 !== 0 && friend.userId1 !== undefined ? friend.userId1 : friend.userId2) || 0;
    }
    if (friendId === 0) {
      friendId = (friend.user_id_1 !== 0 && friend.user_id_1 !== undefined ? friend.user_id_1 : friend.user_id_2) || 0;
    }

    if (friendId === 0) {
      this.error = 'Error: Could not determine friend ID';
      return;
    }

    if (!confirm('Remove this friend?')) {
      return;
    }

    this.api.removeFriend(friendId).subscribe({
      next: () => {
        this.friends = this.friends.filter(f =>
          !((f.userId1 === friendId || f.userId2 === friendId) ||
            (f.user_id_1 === friendId || f.user_id_2 === friendId))
        );
        this.successMessage = 'Friend removed';
        this.error = null;
        setTimeout(() => {
          this.successMessage = null;
        }, 2000);
      },
      error: (e) => {
        console.error('Failed to remove friend', e);
        this.error = e?.error?.detail || 'Failed to remove friend';
        this.successMessage = null;
      }
    });
  }

  // ---------- TRIP INVITES ----------

  /**
   * Load incoming trip invites for the current user.
   * Backend already returns only "pending" invites.
   */
  loadTripInvites(): void {
    this.loadingTripInvites = true;
    this.api.getTripInvites().subscribe({
      next: (invites) => {
        this.tripInvites = (invites || []).filter(i => i.status === 'pending');
        this.loadingTripInvites = false;
      },
      error: (e) => {
        console.error('Failed to load trip invites', e);
        this.loadingTripInvites = false;
      }
    });
  }

  /**
   * Respond to a trip invite (accept or decline).
   * When accepted, backend adds the user as a participant.
   */
  respondToTripInvite(invite: TripInvite, action: 'accepted' | 'declined'): void {
    if (invite.status !== 'pending') {
      return;
    }

    this.api.respondToTripInvite(invite.id, action).subscribe({
      next: (updated) => {
        // Remove invite from local list
        this.tripInvites = this.tripInvites.filter(i => i.id !== invite.id);

        if (action === 'accepted') {
          this.successMessage = `You joined the trip: ${updated.tripName || 'Trip #' + updated.tripId}`;
        } else {
          this.successMessage = 'Trip invite has been declined.';
        }
        this.error = null;

        setTimeout(() => {
          this.successMessage = null;
        }, 3000);
      },
      error: (e) => {
        console.error('Error while responding to trip invite', e);
        this.error = e?.error?.detail || 'Could not send a response to the trip invite.';
        this.successMessage = null;
      }
    });
  }

  // ---------- HELPERS ----------

  getInitials(username: string | undefined): string {
    if (!username) return 'FR';
    return username.substring(0, 2).toUpperCase();
  }

  /**
   * Returns the ID of the "other" user in a friendship
   * (not the currently logged-in user).
   */
  getOtherFriendId(friend: Friend): number {
    if (!this.currentUser) {
      return (
        (friend.userId1 !== 0 && friend.userId1 !== undefined ? friend.userId1 :
          friend.userId2 !== 0 && friend.userId2 !== undefined ? friend.userId2 :
            friend.user_id_1 !== 0 && friend.user_id_1 !== undefined ? friend.user_id_1 :
              friend.user_id_2) || 0
      );
    }

    const userId1 = friend.userId1 || friend.user_id_1;
    const userId2 = friend.userId2 || friend.user_id_2;

    if (this.currentUser.id === userId1) {
      return userId2 || 0;
    }
    return userId1 || 0;
  }
}
