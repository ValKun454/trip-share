import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { AuthService } from '../../core/services/auth.service';

interface Friend {
  uid: string;
  username?: string;
  email?: string;
  addedAt?: string;
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
  private auth = inject(AuthService);
  private fb = inject(FormBuilder);

  friends: Friend[] = [];
  loading = false;
  error: string | null = null;
  successMessage: string | null = null;

  addFriendForm: FormGroup;

  constructor() {
    this.addFriendForm = this.fb.group({
      uid: ['', [Validators.required, Validators.minLength(3)]]
    });
  }

  ngOnInit(): void {
    this.loadFriends();
  }

  loadFriends(): void {
    this.loading = true;
    this.error = null;
    
    // Simulate loading friends from localStorage or backend
    // In real implementation, this would call an API endpoint
    const stored = localStorage.getItem('userFriends');
    if (stored) {
      this.friends = JSON.parse(stored);
    } else {
      this.friends = [];
    }
    this.loading = false;
  }

  addFriend(): void {
    if (this.addFriendForm.invalid) {
      this.addFriendForm.markAllAsTouched();
      return;
    }

    const uid = this.addFriendForm.get('uid')?.value?.trim();

    // Check if friend already exists
    if (this.friends.some(f => f.uid === uid)) {
      this.error = 'This friend is already in your list';
      this.successMessage = null;
      return;
    }

    // Check if trying to add self
    const currentUser = this.auth.getCurrentUser();
    if (currentUser && currentUser.uid === uid) {
      this.error = 'You cannot add yourself as a friend';
      this.successMessage = null;
      return;
    }

    // Add friend (in real app, would call backend to verify UID exists)
    const newFriend: Friend = {
      uid,
      addedAt: new Date().toISOString()
    };

    this.friends.push(newFriend);
    
    // Save to localStorage
    localStorage.setItem('userFriends', JSON.stringify(this.friends));

    this.successMessage = `Friend with UID "${uid}" added successfully!`;
    this.error = null;
    this.addFriendForm.reset();

    // Clear success message after 3 seconds
    setTimeout(() => {
      this.successMessage = null;
    }, 3000);
  }

  removeFriend(uid: string): void {
    this.friends = this.friends.filter(f => f.uid !== uid);
    localStorage.setItem('userFriends', JSON.stringify(this.friends));
    this.successMessage = `Friend removed`;
    setTimeout(() => {
      this.successMessage = null;
    }, 2000);
  }

  getInitials(uid: string): string {
    return uid.substring(0, 2).toUpperCase();
  }
}
