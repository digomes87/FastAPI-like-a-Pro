import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(
    private notificationService: NotificationService,
    private router: Router,
    private authService: AuthService
  ) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      retry(1), // Retry failed requests once
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'Ocorreu um erro inesperado';
        
        if (error.error instanceof ErrorEvent) {
          // Client-side error
          errorMessage = `Erro: ${error.error.message}`;
        } else {
          // Server-side error
          switch (error.status) {
            case 400:
              errorMessage = this.handleBadRequest(error);
              break;
            case 401:
              errorMessage = 'Não autorizado. Faça login novamente.';
              this.handleUnauthorized();
              break;
            case 403:
              errorMessage = 'Acesso negado. Você não tem permissão para esta ação.';
              break;
            case 404:
              errorMessage = 'Recurso não encontrado.';
              break;
            case 409:
              errorMessage = this.handleConflict(error);
              break;
            case 422:
              errorMessage = this.handleValidationError(error);
              break;
            case 429:
              errorMessage = 'Muitas tentativas. Tente novamente mais tarde.';
              break;
            case 500:
              errorMessage = 'Erro interno do servidor. Tente novamente mais tarde.';
              break;
            case 502:
              errorMessage = 'Serviço temporariamente indisponível.';
              break;
            case 503:
              errorMessage = 'Serviço em manutenção. Tente novamente mais tarde.';
              break;
            default:
              if (error.status >= 500) {
                errorMessage = 'Erro do servidor. Tente novamente mais tarde.';
              } else if (error.status >= 400) {
                errorMessage = 'Erro na solicitação. Verifique os dados e tente novamente.';
              }
              break;
          }
        }

        // Show error message (except for 401 which is handled separately)
        if (error.status !== 401) {
          this.showErrorMessage(errorMessage);
        }

        // Log error for debugging
        console.error('HTTP Error:', {
          status: error.status,
          message: error.message,
          url: error.url,
          error: error.error
        });

        return throwError(() => error);
      })
    );
  }

  private handleBadRequest(error: HttpErrorResponse): string {
    if (error.error?.detail) {
      if (typeof error.error.detail === 'string') {
        return error.error.detail;
      } else if (Array.isArray(error.error.detail)) {
        // Handle validation errors from FastAPI
        const validationErrors = error.error.detail
          .map((err: any) => `${err.loc?.join(' → ') || 'Campo'}: ${err.msg}`)
          .join(', ');
        return `Erro de validação: ${validationErrors}`;
      }
    }
    return 'Dados inválidos. Verifique os campos e tente novamente.';
  }

  private handleConflict(error: HttpErrorResponse): string {
    if (error.error?.detail) {
      return error.error.detail;
    }
    return 'Conflito de dados. O recurso já existe ou está sendo usado.';
  }

  private handleValidationError(error: HttpErrorResponse): string {
    if (error.error?.detail) {
      if (Array.isArray(error.error.detail)) {
        const validationErrors = error.error.detail
          .map((err: any) => {
            const field = err.loc?.slice(1).join(' → ') || 'Campo';
            return `${field}: ${err.msg}`;
          })
          .join('\n');
        return `Erro de validação:\n${validationErrors}`;
      }
      return error.error.detail;
    }
    return 'Dados inválidos. Verifique os campos e tente novamente.';
  }

  private handleUnauthorized(): void {
    // Clear authentication data
    this.authService.logout();
    
    // Redirect to login page
    this.router.navigate(['/auth/login'], {
      queryParams: { returnUrl: this.router.url }
    });
    
    // Show login message
    this.showErrorMessage('Sua sessão expirou. Faça login novamente.');
  }

  private showErrorMessage(message: string): void {
    this.notificationService.showError(message);
  }
}