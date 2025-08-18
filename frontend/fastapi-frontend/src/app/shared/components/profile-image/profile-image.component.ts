import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ImageService } from '../../../core/services/image.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-profile-image',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatTooltipModule
  ],
  template: `
    <div class="profile-image-container">
      <div class="image-wrapper" [class.clickable]="showSelector">
        <img 
          [src]="currentImage" 
          [alt]="altText"
          class="profile-image"
          [class.size-small]="size === 'small'"
          [class.size-medium]="size === 'medium'"
          [class.size-large]="size === 'large'"
          (error)="onImageError($event)"
          (click)="showSelector && toggleSelector()"
        />
        
        <!-- Overlay para seleção -->
        <div class="image-overlay" *ngIf="showSelector" (click)="toggleSelector()">
          <mat-icon>camera_alt</mat-icon>
        </div>
      </div>

      <!-- Menu de seleção de imagens -->
      <div class="image-selector" *ngIf="showSelector && selectorOpen">
        <div class="selector-header">
          <h3>Escolha sua foto de perfil</h3>
          <button mat-icon-button (click)="closeSelectorMenu()">
            <mat-icon>close</mat-icon>
          </button>
        </div>
        
        <div class="image-grid">
          <div 
            class="image-option" 
            *ngFor="let image of availableImages"
            (click)="selectImage(image)"
            [class.selected]="image === currentImage"
          >
            <img [src]="image" [alt]="'Opção de imagem'" />
          </div>
          
          <!-- Opção para gerar nova imagem aleatória -->
          <div class="image-option random-option" (click)="generateRandomImage()">
            <mat-icon>shuffle</mat-icon>
            <span>Aleatória</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./profile-image.component.scss']
})
export class ProfileImageComponent implements OnInit, OnDestroy {
  @Input() size: 'small' | 'medium' | 'large' = 'medium';
  @Input() showSelector: boolean = false;
  @Input() altText: string = 'Imagem de perfil';
  @Output() imageChanged = new EventEmitter<string>();

  currentImage: string = '';
  availableImages: string[] = [];
  selectorOpen: boolean = false;
  private subscription: Subscription = new Subscription();

  constructor(private imageService: ImageService) {}

  ngOnInit(): void {
    // Inscrever-se nas mudanças da imagem de perfil
    this.subscription.add(
      this.imageService.profileImage$.subscribe(image => {
        this.currentImage = image;
        this.imageChanged.emit(image);
      })
    );

    // Carregar imagens disponíveis se o seletor estiver habilitado
    if (this.showSelector) {
      this.availableImages = this.imageService.getAvailableProfileImages();
    }
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  toggleSelector(): void {
    if (this.showSelector) {
      this.selectorOpen = !this.selectorOpen;
    }
  }

  closeSelectorMenu(): void {
    this.selectorOpen = false;
  }

  selectImage(imageUrl: string): void {
    this.imageService.setProfileImage(imageUrl);
    this.selectorOpen = false;
  }

  generateRandomImage(): void {
    this.imageService.generateNewProfileImage();
    this.selectorOpen = false;
  }

  onImageError(event: any): void {
    // Fallback para uma imagem padrão em caso de erro
    event.target.src = 'https://via.placeholder.com/400x400/cccccc/666666?text=Perfil';
  }
}