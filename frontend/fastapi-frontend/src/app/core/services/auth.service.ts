import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, tap, catchError, throwError } from 'rxjs';
import { LoginRequest, LoginResponse, AuthState, GoogleAuthResponse } from '../models/auth';
import { User } from '../models/user';
import { ImageService } from './image.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = 'http://localhost:8000';
  private readonly TOKEN_KEY = 'access_token';
  
  private authStateSubject = new BehaviorSubject<AuthState>({
    isAuthenticated: false,
    token: null,
    user: null
  });
  
  public authState$ = this.authStateSubject.asObservable();

  constructor(
    private http: HttpClient,
    private imageService: ImageService
  ) {
    this.initializeAuthState();
  }

  private initializeAuthState(): void {
    // Only initialize on browser side
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      const token = this.getStoredToken();
      if (token && !this.isTokenExpired(token)) {
        this.authStateSubject.next({
          isAuthenticated: true,
          token: token,
          user: null // Will be loaded separately
        });
      }
    }
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<LoginResponse>(`${this.API_URL}/auth/token`, formData)
      .pipe(
        tap(response => {
          this.setToken(response.access_token);
          // Carregar imagem de perfil salva após login bem-sucedido
          this.loadSavedProfileImage();
          this.authStateSubject.next({
            isAuthenticated: true,
            token: response.access_token,
            user: null
          });
        }),
        catchError(error => {
          console.error('Login error:', error);
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    this.removeToken();
    // Limpar imagem de perfil ao fazer logout
    this.imageService.clearStoredProfileImage();
    this.authStateSubject.next({
      isAuthenticated: false,
      token: null,
      user: null
    });
  }

  getGoogleAuthUrl(): Observable<{authorization_url: string, message: string}> {
    return this.http.get<{authorization_url: string, message: string}>(`${this.API_URL}/auth/google/login`)
      .pipe(
        catchError(error => {
          console.error('Google auth URL error:', error);
          return throwError(() => error);
        })
      );
  }

  handleGoogleCallback(code: string): Observable<LoginResponse> {
    return this.http.get<LoginResponse>(`${this.API_URL}/auth/google/callback?code=${code}`)
      .pipe(
        tap(response => {
          this.setToken(response.access_token);
          // Carregar imagem de perfil salva após login bem-sucedido
          this.loadSavedProfileImage();
          this.authStateSubject.next({
            isAuthenticated: true,
            token: response.access_token,
            user: null
          });
        }),
        catchError(error => {
          console.error('Google callback error:', error);
          return throwError(() => error);
        })
      );
  }

  loginWithGoogle(): void {
    this.getGoogleAuthUrl().subscribe({
      next: (response) => {
        // Redirecionar para a URL de autorização do Google
        window.location.href = response.authorization_url;
      },
      error: (error) => {
        console.error('Erro ao obter URL de autorização do Google:', error);
      }
    });
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/users/me`, {
      headers: this.getAuthHeaders()
    }).pipe(
      tap(user => {
        const currentState = this.authStateSubject.value;
        this.authStateSubject.next({
          ...currentState,
          user: user
        });
      }),
      catchError(error => {
        console.error('Get current user error:', error);
        if (error.status === 401) {
          this.logout();
        }
        return throwError(() => error);
      })
    );
  }

  isAuthenticated(): boolean {
    const token = this.getStoredToken();
    return token !== null && !this.isTokenExpired(token);
  }

  getToken(): string | null {
    return this.getStoredToken();
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      localStorage.setItem(this.TOKEN_KEY, token);
    }
  }

  private removeToken(): void {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      localStorage.removeItem(this.TOKEN_KEY);
    }
  }

  private getStoredToken(): string | null {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      return localStorage.getItem(this.TOKEN_KEY);
    }
    return null;
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000; // Convert to milliseconds
      return Date.now() >= exp;
    } catch (error) {
      return true;
    }
  }

  private getAuthHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  private loadSavedProfileImage(): void {
    // O ImageService já carrega automaticamente a imagem salva na inicialização
    // Este método pode ser usado para forçar o recarregamento se necessário
    const savedImage = this.imageService.getCurrentProfileImage();
    if (savedImage) {
      console.log('Imagem de perfil carregada:', savedImage);
    }
  }
}
