import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { LoadingService } from '../services/loading.service';

@Injectable()
export class LoadingInterceptor implements HttpInterceptor {
  private totalRequests = 0;

  constructor(private loadingService: LoadingService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Check if this request should show loading indicator
    if (this.shouldShowLoading(request)) {
      this.totalRequests++;
      this.loadingService.setLoading(true);
    }

    return next.handle(request).pipe(
      finalize(() => {
        if (this.shouldShowLoading(request)) {
          this.totalRequests--;
          if (this.totalRequests === 0) {
            this.loadingService.setLoading(false);
          }
        }
      })
    );
  }

  private shouldShowLoading(request: HttpRequest<any>): boolean {
    // Don't show loading for certain requests
    const skipLoadingEndpoints = [
      '/auth/refresh', // Token refresh should be silent
      '/health', // Health checks
      '/ping' // Ping requests
    ];

    // Check if request has custom header to skip loading
    if (request.headers.has('X-Skip-Loading')) {
      return false;
    }

    // Check if URL should skip loading
    return !skipLoadingEndpoints.some(endpoint => 
      request.url.includes(endpoint)
    );
  }
}