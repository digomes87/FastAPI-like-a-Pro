import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Get the auth token from the service
    const authToken = this.authService.getToken();
    
    // Check if we should add the authorization header
    if (authToken && this.shouldAddAuthHeader(request.url)) {
      // Clone the request and add the authorization header
      const authRequest = request.clone({
        setHeaders: {
          Authorization: `Bearer ${authToken}`
        }
      });
      
      return next.handle(authRequest);
    }
    
    // If no token or shouldn't add auth header, proceed with original request
    return next.handle(request);
  }

  private shouldAddAuthHeader(url: string): boolean {
    // List of endpoints that don't need authentication
    const publicEndpoints = [
      '/auth/login',
      '/auth/register',
      '/auth/google',
      '/auth/refresh'
    ];
    
    // Check if the URL is a public endpoint
    const isPublicEndpoint = publicEndpoints.some(endpoint => 
      url.includes(endpoint)
    );
    
    // Don't add auth header for public endpoints
    return !isPublicEndpoint;
  }
}