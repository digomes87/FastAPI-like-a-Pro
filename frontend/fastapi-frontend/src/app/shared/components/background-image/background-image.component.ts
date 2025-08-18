import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ImageService } from '../../../core/services/image.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-background-image',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div 
      class="background-container"
      [style.background-image]="'url(' + currentBackgroundImage + ')'"
      [class.overlay]="showOverlay"
      [class.blur]="blurBackground"
    >
      <div class="background-overlay" *ngIf="showOverlay"></div>
      <ng-content></ng-content>
    </div>
  `,
  styleUrls: ['./background-image.component.scss']
})
export class BackgroundImageComponent implements OnInit, OnDestroy {
  @Input() showOverlay: boolean = true;
  @Input() blurBackground: boolean = false;
  @Input() overlayOpacity: number = 0.3;

  currentBackgroundImage: string = '';
  private subscription: Subscription = new Subscription();

  constructor(private imageService: ImageService) {}

  ngOnInit(): void {
    // Inscrever-se nas mudanças da imagem de fundo
    this.subscription.add(
      this.imageService.backgroundImage$.subscribe(image => {
        this.currentBackgroundImage = image;
      })
    );
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }
}