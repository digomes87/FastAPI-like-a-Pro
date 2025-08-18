import { Injectable } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private defaultConfig: MatSnackBarConfig = {
    duration: 5000,
    horizontalPosition: 'end',
    verticalPosition: 'top'
  };

  constructor(private snackBar: MatSnackBar) {}

  showSuccess(message: string, action?: string, config?: MatSnackBarConfig): void {
    const successConfig = {
      ...this.defaultConfig,
      panelClass: 'success-snackbar',
      ...config
    };
    
    this.snackBar.open(message, action || 'Fechar', successConfig);
  }

  showError(message: string, action?: string, config?: MatSnackBarConfig): void {
    const errorConfig = {
      ...this.defaultConfig,
      duration: 8000, // Longer duration for errors
      panelClass: 'error-snackbar',
      ...config
    };
    
    this.snackBar.open(message, action || 'Fechar', errorConfig);
  }

  showWarning(message: string, action?: string, config?: MatSnackBarConfig): void {
    const warningConfig = {
      ...this.defaultConfig,
      duration: 6000,
      panelClass: 'warning-snackbar',
      ...config
    };
    
    this.snackBar.open(message, action || 'Fechar', warningConfig);
  }

  showInfo(message: string, action?: string, config?: MatSnackBarConfig): void {
    const infoConfig = {
      ...this.defaultConfig,
      panelClass: 'info-snackbar',
      ...config
    };
    
    this.snackBar.open(message, action || 'Fechar', infoConfig);
  }

  dismiss(): void {
    this.snackBar.dismiss();
  }
}