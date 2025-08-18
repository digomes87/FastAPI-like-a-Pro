import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../core/services/auth.service';
import { UserService } from '../../core/services/user.service';
import { ImageService } from '../../core/services/image.service';
import { User } from '../../core/models/user';
import { ProfileImageComponent } from '../../shared/components/profile-image/profile-image.component';
import { BackgroundImageComponent } from '../../shared/components/background-image/background-image.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    MatGridListModule,
    MatSnackBarModule,
    ProfileImageComponent,
    BackgroundImageComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  currentUser: User | null = null;
  isLoading = true;

  constructor(
    private authService: AuthService,
    private userService: UserService,
    private imageService: ImageService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadCurrentUser();
  }

  private loadCurrentUser(): void {
    this.isLoading = true;
    this.userService.getCurrentUser().subscribe({
      next: (user) => {
        this.currentUser = user;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('Erro ao carregar usuário:', error);
        this.snackBar.open('Erro ao carregar dados do usuário', 'Fechar', {
          duration: 3000,
          panelClass: ['error-snackbar']
        });
        this.isLoading = false;
      }
    });
  }

  navigateToUsers(): void {
    this.router.navigate(['/users']);
  }

  navigateToProfile(): void {
    this.router.navigate(['/users/profile']);
  }

  logout(): void {
    try {
      this.authService.logout();
      this.snackBar.open('Logout realizado com sucesso', 'Fechar', {
        duration: 2000,
        panelClass: ['success-snackbar']
      });
      this.router.navigate(['/login']);
    } catch (error: any) {
      console.error('Erro no logout:', error);
      // Mesmo com erro, redireciona para login
      this.router.navigate(['/login']);
    }
  }

  getWelcomeMessage(): string {
    const hour = new Date().getHours();
    if (hour < 12) {
      return 'Bom dia';
    } else if (hour < 18) {
      return 'Boa tarde';
    } else {
      return 'Boa noite';
    }
  }

  formatDate(date: string | undefined): string {
    if (!date) {
      return 'Data não disponível';
    }
    return new Date(date).toLocaleDateString('pt-BR');
  }

  onProfileImageChanged(imageUrl: string): void {
    // A imagem já foi persistida pelo ImageService
    // Aqui podemos adicionar lógica adicional se necessário
    console.log('Imagem de perfil alterada:', imageUrl);
  }
}
