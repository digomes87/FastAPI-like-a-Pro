import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, NavigationEnd } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AuthService } from '../../../core/services/auth.service';
import { UserService } from '../../../core/services/user.service';
import { User } from '../../../core/models/user';
import { filter } from 'rxjs/operators';

interface MenuItem {
  label: string;
  icon: string;
  route: string;
  tooltip?: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule,
    MatTooltipModule
  ],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent implements OnInit {
  @Input() isOpen = false;
  @Input() mode: 'over' | 'side' = 'side';
  @Output() closeSidebar = new EventEmitter<void>();

  currentUser: User | null = null;
  currentRoute = '';
  
  menuItems: MenuItem[] = [
    {
      label: 'Dashboard',
      icon: 'dashboard',
      route: '/dashboard',
      tooltip: 'Painel principal'
    },
    {
      label: 'Usuários',
      icon: 'people',
      route: '/users',
      tooltip: 'Gerenciar usuários'
    },
    {
      label: 'Meu Perfil',
      icon: 'account_circle',
      route: '/users/profile',
      tooltip: 'Visualizar e editar perfil'
    }
  ];

  constructor(
    private authService: AuthService,
    private userService: UserService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadCurrentUser();
    this.trackCurrentRoute();
  }

  private loadCurrentUser(): void {
    if (this.authService.isAuthenticated()) {
      this.userService.getCurrentUser().subscribe({
        next: (user) => {
          this.currentUser = user;
        },
        error: (error: any) => {
          console.error('Erro ao carregar usuário:', error);
        }
      });
    }
  }

  private trackCurrentRoute(): void {
    // Get current route
    this.currentRoute = this.router.url;
    
    // Track route changes
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.currentRoute = event.url;
      });
  }

  navigateTo(route: string): void {
    this.router.navigate([route]);
    if (this.mode === 'over') {
      this.closeSidebar.emit();
    }
  }

  isActiveRoute(route: string): boolean {
    if (route === '/dashboard') {
      return this.currentRoute === '/' || this.currentRoute === '/dashboard';
    }
    return this.currentRoute.startsWith(route);
  }

  onCloseSidebar(): void {
    this.closeSidebar.emit();
  }

  getUserInitials(): string {
    if (this.currentUser?.username) {
      return this.currentUser.username.substring(0, 2).toUpperCase();
    }
    return 'U';
  }

  logout(): void {
    try {
      this.authService.logout();
      this.router.navigate(['/login']);
      if (this.mode === 'over') {
        this.closeSidebar.emit();
      }
    } catch (error: any) {
      console.error('Erro no logout:', error);
      this.router.navigate(['/login']);
    }
  }
}
