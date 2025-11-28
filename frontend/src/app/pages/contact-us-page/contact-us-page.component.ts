import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from "@angular/forms";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatButtonModule } from "@angular/material/button";
import { MatCardModule } from "@angular/material/card";
import { MatIconModule } from "@angular/material/icon";
import { MatSnackBar, MatSnackBarModule } from "@angular/material/snack-bar";

@Component({
  selector: "app-contact-us-page",
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatSnackBarModule
  ],
  templateUrl: "./contact-us-page.component.html",
  styleUrls: ["./contact-us-page.component.css"]
})
export class ContactUsPageComponent {
  contactForm: FormGroup;

  // Contact Information
  contactInfo = {
    phone: "+48 777 777 777",
    email: "info@tripshare.com",
    address: "Wydział Fizyki i Astronomii UAM, ul. Uniwersytetu Poznańskiego 2, 61-614 Poznań"
  };

  // Head of Contact Information (карточку мы убрали из шаблона, но объект оставляем — не мешает)
  headOfContact = {
    name: "Sarah Johnson",
    title: "Director of Customer Relations",
    phone: "+1 (555) 123-4568",
    email: "sarah.johnson@tripshare.com",
    photo: "assets/images/sarah-johnson.jpg",
    bio: "Sarah has over 10 years of experience in travel industry and customer service. She's passionate about helping travelers create unforgettable experiences."
  };

  // Office location for map (в шаблоне сейчас не используется)
  officeLocation = {
    lat: 40.7589,
    lng: -73.9851,
    address: "123 Travel Street, Adventure City, AC 12345"
  };

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar
  ) {
    this.contactForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', [Validators.pattern(/^[\+]?[1-9][\d]{0,15}$/)]],
      subject: ['', [Validators.required, Validators.minLength(3)]],
      message: ['', [Validators.required, Validators.minLength(10)]]
    });
  }

  onSubmit() {
    if (this.contactForm.valid) {
      console.log('Contact form submitted:', this.contactForm.value);

      this.snackBar.open('Thank you for your message! We\'ll get back to you soon.', 'Close', {
        duration: 5000,
        panelClass: ['success-snackbar']
      });

      this.contactForm.reset();
    } else {
      this.markFormGroupTouched();
      this.snackBar.open('Please fill in all required fields correctly.', 'Close', {
        duration: 3000,
        panelClass: ['error-snackbar']
      });
    }
  }

  private markFormGroupTouched() {
    Object.keys(this.contactForm.controls).forEach(key => {
      const control = this.contactForm.get(key);
      control?.markAsTouched();
    });
  }

  getErrorMessage(fieldName: string): string {
    const control = this.contactForm.get(fieldName);
    if (control?.hasError('required')) {
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required`;
    }
    if (control?.hasError('email')) {
      return 'Please enter a valid email address';
    }
    if (control?.hasError('minlength')) {
      const requiredLength = control.errors?.['minlength']?.requiredLength;
      return `Minimum ${requiredLength} characters required`;
    }
    if (control?.hasError('pattern')) {
      return 'Please enter a valid phone number';
    }
    return '';
  }
}
