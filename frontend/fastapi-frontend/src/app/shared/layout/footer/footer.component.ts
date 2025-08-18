import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule
  ],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.scss'
})
export class FooterComponent {
  currentYear = new Date().getFullYear();
  appVersion = '1.0.0';
  
  constructor() {}

  openGitHub(): void {
    window.open('https://github.com', '_blank');
  }

  openDocumentation(): void {
    // Placeholder for documentation link
    console.log('Abrir documentação');
  }

  openSupport(): void {
    // Placeholder for support link
    console.log('Abrir suporte');
  }
}