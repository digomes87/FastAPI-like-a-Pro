import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { User, UserCreate, UserUpdate, UserResponse } from '../models/user';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly API_URL = 'http://localhost:8000';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  getUsers(skip: number = 0, limit: number = 100): Observable<User[]> {
    return this.http.get<User[]>(`${this.API_URL}/users/?skip=${skip}&limit=${limit}`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(error => {
        console.error('Get users error:', error);
        return throwError(() => error);
      })
    );
  }

  getUserById(userId: number): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/users/${userId}`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(error => {
        console.error('Get user by ID error:', error);
        return throwError(() => error);
      })
    );
  }

  createUser(userData: UserCreate): Observable<UserResponse> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    return this.http.post<UserResponse>(`${this.API_URL}/users/`, userData, {
      headers: headers
    }).pipe(
      catchError(error => {
        console.error('Create user error:', error);
        return throwError(() => error);
      })
    );
  }

  updateUser(userId: number, userData: UserUpdate): Observable<UserResponse> {
    return this.http.put<UserResponse>(`${this.API_URL}/users/${userId}`, userData, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(error => {
        console.error('Update user error:', error);
        return throwError(() => error);
      })
    );
  }

  deleteUser(userId: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.API_URL}/users/${userId}`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(error => {
        console.error('Delete user error:', error);
        return throwError(() => error);
      })
    );
  }

  getCurrentUser(): Observable<User> {
    return this.authService.getCurrentUser();
  }

  private getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }
}
