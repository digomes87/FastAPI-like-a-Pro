import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-google-callback',
  standalone: true,
  imports: [
    CommonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule
  ],
  template: `
    <div class="callback-container">
      <div class="callback-content">
        <mat-spinner diameter="50"></mat-spinner>
        <h2>Processando login com Google...</h2>
        <p>Aguarde enquanto validamos suas credenciais.</p>
      </div>
    </div>
  `,
  styles: [`
    .callback-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .callback-content {
      text-align: center;
      color: white;
      padding: 40px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    h2 {
      margin: 20px 0 10px;
      font-size: 24px;
      font-weight: 500;
    }
    
    p {
      margin: 0;
      opacity: 0.8;
      font-size: 16px;
    }
  `]
})
export class GoogleCallbackComponent implements OnInit {

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.handleGoogleCallback();
  }

  private handleGoogleCallback(): void {
    this.route.queryParams.subscribe(params => {
      const code = params['code'];
      const error = params['error'];

      if (error) {
        this.showError('Erro na autenticação com Google: ' + error);
        this.router.navigate(['/login']);
        return;
      }

      if (!code) {
        this.showError('Código de autorização não encontrado');
        this.router.navigate(['/login']);
        return;
      }

      // Processar o callback do Google
      this.authService.handleGoogleCallback(code).subscribe({
        next: (response) => {
          this.showSuccess('Login realizado com sucesso!');
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          console.error('Erro no callback do Google:', error);
          this.showError('Erro ao processar login com Google');
          this.router.navigate(['/login']);
        }
      });
    });
  }

  private showSuccess(message: string): void {
    this.snackBar.open(message, 'Fechar', {
      duration: 5000,
      panelClass: ['success-snackbar']
    });
  }

  private showError(message: string): void {
    this.snackBar.open(message, 'Fechar', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}