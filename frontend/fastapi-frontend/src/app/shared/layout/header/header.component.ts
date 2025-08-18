import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../../core/services/auth.service';
import { UserService } from '../../../core/services/user.service';
import { User } from '../../../core/models/user';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatTooltipModule,
    MatSnackBarModule
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent implements OnInit {
  @Output() toggleSidebar = new EventEmitter<void>();
  
  currentUser: User | null = null;
  isAuthenticated = false;

  constructor(
    private authService: AuthService,
    private userService: UserService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.checkAuthStatus();
    this.loadCurrentUser();
  }

  private checkAuthStatus(): void {
    this.isAuthenticated = this.authService.isAuthenticated();
  }

  private loadCurrentUser(): void {
    if (this.isAuthenticated) {
      this.userService.getCurrentUser().subscribe({
        next: (user) => {
          this.currentUser = user;
        },
        error: (error: any) => {
          console.error('Erro ao carregar usuário:', error);
        }
      });
    }
  }

  onToggleSidebar(): void {
    this.toggleSidebar.emit();
  }

  navigateToHome(): void {
    if (this.isAuthenticated) {
      this.router.navigate(['/dashboard']);
    } else {
      this.router.navigate(['/login']);
    }
  }

  navigateToProfile(): void {
    this.router.navigate(['/users/profile']);
  }

  navigateToUsers(): void {
    this.router.navigate(['/users']);
  }

  navigateToLogin(): void {
    this.router.navigate(['/login']);
  }

  navigateToRegister(): void {
    this.router.navigate(['/register']);
  }

  logout(): void {
    try {
      this.authService.logout();
      this.currentUser = null;
      this.isAuthenticated = false;
      this.snackBar.open('Logout realizado com sucesso', 'Fechar', {
        duration: 2000,
        panelClass: ['success-snackbar']
      });
      this.router.navigate(['/login']);
    } catch (error: any) {
      console.error('Erro no logout:', error);
      this.router.navigate(['/login']);
    }
  }

  getUserInitials(): string {
    if (this.currentUser?.username) {
      return this.currentUser.username.substring(0, 2).toUpperCase();
    }
    return 'U';
  }
}
