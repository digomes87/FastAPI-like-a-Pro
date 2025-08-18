import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { UserService } from '../../../core/services/user.service';
import { AuthService } from '../../../core/services/auth.service';
import { ImageService } from '../../../core/services/image.service';
import { User } from '../../../core/models/user';
import { ProfileImageComponent } from '../../../shared/components/profile-image/profile-image.component';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDividerModule,
    MatChipsModule,
    MatTooltipModule,
    ProfileImageComponent
  ],
  templateUrl: './user-profile.component.html',
  styleUrl: './user-profile.component.scss'
})
export class UserProfileComponent implements OnInit {
  profileForm: FormGroup;
  user: User | null = null;
  isLoading = false;
  isEditing = false;
  isSaving = false;
  isCurrentUser = false;
  userId: number | null = null;

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private authService: AuthService,
    private imageService: ImageService,
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.profileForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: [''],
      confirmPassword: ['']
    });
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.userId = params['id'] ? parseInt(params['id']) : null;
      this.loadUserProfile();
    });
  }

  loadUserProfile(): void {
    this.isLoading = true;
    
    if (this.userId) {
      // Load specific user by ID
      this.userService.getUserById(this.userId).subscribe({
        next: (user) => {
          this.user = user;
          this.checkIfCurrentUser();
          this.populateForm();
          this.isLoading = false;
        },
        error: (error: any) => {
          console.error('Erro ao carregar usuário:', error);
          this.showMessage('Erro ao carregar perfil do usuário', 'error');
          this.isLoading = false;
          this.router.navigate(['/users']);
        }
      });
    } else {
      // Load current user profile
      this.userService.getCurrentUser().subscribe({
        next: (user) => {
          this.user = user;
          this.isCurrentUser = true;
          this.populateForm();
          this.isLoading = false;
        },
        error: (error: any) => {
          console.error('Erro ao carregar perfil:', error);
          this.showMessage('Erro ao carregar perfil', 'error');
          this.isLoading = false;
          this.router.navigate(['/dashboard']);
        }
      });
    }
  }

  private checkIfCurrentUser(): void {
    if (this.authService.isAuthenticated() && this.user) {
      this.userService.getCurrentUser().subscribe({
        next: (currentUser) => {
          this.isCurrentUser = currentUser.id === this.user?.id;
        },
        error: (error: any) => {
          console.error('Erro ao verificar usuário atual:', error);
        }
      });
    }
  }

  private populateForm(): void {
    if (this.user) {
      this.profileForm.patchValue({
        email: this.user.email,
        password: '',
        confirmPassword: ''
      });
    }
  }

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (!this.isEditing) {
      // Reset form when canceling edit
      this.populateForm();
    }
  }

  onSubmit(): void {
    if (this.profileForm.valid && this.user) {
      const formData = this.profileForm.value;
      
      // Validate password confirmation if password is provided
      if (formData.password && formData.password !== formData.confirmPassword) {
        this.showMessage('As senhas não coincidem', 'error');
        return;
      }

      this.isSaving = true;
      
      const updateData: any = {
        email: formData.email
      };
      
      // Only include password if it's provided
      if (formData.password) {
        updateData.password = formData.password;
      }

      this.userService.updateUser(this.user.id, updateData).subscribe({
        next: (updatedUser) => {
          this.user = updatedUser;
          this.isEditing = false;
          this.isSaving = false;
          this.populateForm();
          this.showMessage('Perfil atualizado com sucesso', 'success');
        },
        error: (error: any) => {
          console.error('Erro ao atualizar perfil:', error);
          this.isSaving = false;
          
          if (error.status === 400) {
            this.showMessage('Dados inválidos. Verifique os campos.', 'error');
          } else if (error.status === 409) {
            this.showMessage('Nome de usuário ou email já existe.', 'error');
          } else {
            this.showMessage('Erro ao atualizar perfil', 'error');
          }
        }
      });
    } else {
      this.markFormGroupTouched();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.profileForm.controls).forEach(key => {
      const control = this.profileForm.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.profileForm.get(fieldName);
    if (field?.errors && field.touched) {
      if (field.errors['required']) {
        return `${this.getFieldLabel(fieldName)} é obrigatório`;
      }
      if (field.errors['email']) {
        return 'Email inválido';
      }
      if (field.errors['minlength']) {
        return `${this.getFieldLabel(fieldName)} deve ter pelo menos ${field.errors['minlength'].requiredLength} caracteres`;
      }
    }
    return '';
  }

  private getFieldLabel(fieldName: string): string {
    const labels: { [key: string]: string } = {
      username: 'Nome de usuário',
      email: 'Email',
      password: 'Senha',
      confirmPassword: 'Confirmação de senha'
    };
    return labels[fieldName] || fieldName;
  }

  getUserInitials(): string {
    if (this.user?.username) {
      return this.user.username.substring(0, 2).toUpperCase();
    }
    return 'U';
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  goBack(): void {
    if (this.userId) {
      this.router.navigate(['/users']);
    } else {
      this.router.navigate(['/dashboard']);
    }
  }

  private showMessage(message: string, type: 'success' | 'error'): void {
    this.snackBar.open(message, 'Fechar', {
      duration: 5000,
      panelClass: type === 'success' ? 'success-snackbar' : 'error-snackbar',
      horizontalPosition: 'end',
      verticalPosition: 'top'
    });
  }

  onProfileImageChanged(imageUrl: string): void {
    console.log('Profile image changed:', imageUrl);
    this.showMessage('Imagem de perfil atualizada com sucesso!', 'success');
  }
}
