import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ImageService {
  private readonly PROFILE_IMAGE_KEY = 'profile_image';
  private readonly BACKGROUND_IMAGE_KEY = 'background_image';
  
  // URLs de imagens aleatórias do Unsplash
  private readonly randomImages = [
    'https://images.unsplash.com/photo-1494790108755-2616c9c0e8e5?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face'
  ];

  // URLs de imagens de fundo
  private readonly backgroundImages = [
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop',
    'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1920&h=1080&fit=crop',
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop',
    'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1920&h=1080&fit=crop',
    'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=1920&h=1080&fit=crop',
    'https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1920&h=1080&fit=crop',
    'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=1920&h=1080&fit=crop',
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&h=1080&fit=crop'
  ];

  private profileImageSubject = new BehaviorSubject<string>(this.getRandomProfileImage());
  private backgroundImageSubject = new BehaviorSubject<string>(this.getRandomBackgroundImage());

  public profileImage$ = this.profileImageSubject.asObservable();
  public backgroundImage$ = this.backgroundImageSubject.asObservable();

  constructor() {
    this.initializeImages();
  }

  private initializeImages(): void {
    // Inicializar imagem de perfil
    const savedProfileImage = this.getStoredProfileImage();
    if (savedProfileImage) {
      this.profileImageSubject.next(savedProfileImage);
    }

    // Sempre gerar nova imagem de fundo a cada inicialização
    this.generateNewBackgroundImage();
  }

  /**
   * Obtém uma imagem de perfil aleatória
   */
  getRandomProfileImage(): string {
    const randomIndex = Math.floor(Math.random() * this.randomImages.length);
    return this.randomImages[randomIndex];
  }

  /**
   * Obtém uma imagem de fundo aleatória
   */
  getRandomBackgroundImage(): string {
    const randomIndex = Math.floor(Math.random() * this.backgroundImages.length);
    return this.backgroundImages[randomIndex];
  }

  /**
   * Define a imagem de perfil do usuário
   */
  setProfileImage(imageUrl: string): void {
    this.profileImageSubject.next(imageUrl);
    this.saveProfileImage(imageUrl);
  }

  /**
   * Obtém a imagem de perfil atual
   */
  getCurrentProfileImage(): string {
    return this.profileImageSubject.value;
  }

  /**
   * Obtém a imagem de fundo atual
   */
  getCurrentBackgroundImage(): string {
    return this.backgroundImageSubject.value;
  }

  /**
   * Gera uma nova imagem de fundo aleatória
   */
  generateNewBackgroundImage(): void {
    const newBackgroundImage = this.getRandomBackgroundImage();
    this.backgroundImageSubject.next(newBackgroundImage);
  }

  /**
   * Obtém todas as imagens de perfil disponíveis
   */
  getAvailableProfileImages(): string[] {
    return [...this.randomImages];
  }

  /**
   * Salva a imagem de perfil no localStorage
   */
  private saveProfileImage(imageUrl: string): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(this.PROFILE_IMAGE_KEY, imageUrl);
    }
  }

  /**
   * Recupera a imagem de perfil salva do localStorage
   */
  private getStoredProfileImage(): string | null {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem(this.PROFILE_IMAGE_KEY);
    }
    return null;
  }

  /**
   * Remove a imagem de perfil salva
   */
  clearStoredProfileImage(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(this.PROFILE_IMAGE_KEY);
    }
    this.profileImageSubject.next(this.getRandomProfileImage());
  }

  /**
   * Gera uma nova imagem de perfil aleatória
   */
  generateNewProfileImage(): void {
    const newProfileImage = this.getRandomProfileImage();
    this.setProfileImage(newProfileImage);
  }
}