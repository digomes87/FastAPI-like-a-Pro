import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { UserService } from '../../../core/services/user.service';
import { UserCreate } from '../../../core/models/user';

@Component({
  selector: 'app-register',
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
    MatSnackBarModule
  ],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  isLoading = false;
  hidePassword = true;
  hideConfirmPassword = true;

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.initializeForm();
  }

  private initializeForm(): void {
    this.registerForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8), this.passwordValidator]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  private passwordValidator(control: AbstractControl): { [key: string]: any } | null {
    const password = control.value;
    if (!password) return null;

    const errors: any = {};
    
    // Check for uppercase letter
    if (!/[A-Z]/.test(password)) {
      errors.missingUppercase = true;
    }
    
    // Check for lowercase letter
    if (!/[a-z]/.test(password)) {
      errors.missingLowercase = true;
    }
    
    // Check for digit
    if (!/\d/.test(password)) {
      errors.missingDigit = true;
    }
    
    // Check for special character
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.missingSpecialChar = true;
    }
    
    // Check for sequential characters
    if (/123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz/i.test(password)) {
      errors.hasSequentialChars = true;
    }
    
    return Object.keys(errors).length > 0 ? errors : null;
  }

  private passwordMatchValidator(control: AbstractControl): { [key: string]: any } | null {
    const password = control.get('password');
    const confirmPassword = control.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    return null;
  }

  onSubmit(): void {
    if (this.registerForm.valid && !this.isLoading) {
      this.isLoading = true;
      const userData: UserCreate = {
        username: this.registerForm.value.username,
        email: this.registerForm.value.email,
        password: this.registerForm.value.password
      };

      this.userService.createUser(userData).subscribe({
        next: (response) => {
          this.snackBar.open('Conta criada com sucesso! Faça login para continuar.', 'Fechar', {
            duration: 5000,
            panelClass: ['success-snackbar']
          });
          this.router.navigate(['/login']);
        },
        error: (error) => {
          this.isLoading = false;
          let errorMessage = 'Erro ao criar conta. Tente novamente.';
          
          if (error.status === 400) {
            errorMessage = 'Dados inválidos. Verifique os campos preenchidos.';
          } else if (error.status === 409) {
            errorMessage = 'Usuário ou email já existe. Tente com outros dados.';
          } else if (error.status === 422) {
            // Handle detailed validation errors from backend
            if (error.error?.detail && Array.isArray(error.error.detail)) {
              const passwordError = error.error.detail.find((err: any) => err.loc?.includes('password'));
              if (passwordError) {
                errorMessage = 'Senha não atende aos requisitos de segurança. Verifique as regras de senha.';
              } else {
                errorMessage = 'Dados inválidos. Verifique os campos preenchidos.';
              }
            } else {
              errorMessage = 'Dados inválidos. Verifique os campos preenchidos.';
            }
          }
          
          this.snackBar.open(errorMessage, 'Fechar', {
            duration: 7000,
            panelClass: ['error-snackbar']
          });
        },
        complete: () => {
          this.isLoading = false;
        }
      });
    }
  }

  togglePasswordVisibility(): void {
    this.hidePassword = !this.hidePassword;
  }

  toggleConfirmPasswordVisibility(): void {
    this.hideConfirmPassword = !this.hideConfirmPassword;
  }

  goToLogin(): void {
    this.router.navigate(['/login']);
  }
}
