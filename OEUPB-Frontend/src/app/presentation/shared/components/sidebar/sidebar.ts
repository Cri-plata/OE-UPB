import { ChangeDetectorRef, Component, HostListener, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavigationStart, Router, RouterModule } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { filter } from 'rxjs';
import { SidebarService } from '../../services/sidebar.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterModule, CommonModule],
  templateUrl: './sidebar.html',
  styleUrls: ['./sidebar.scss']
})
export class SidebarComponent implements OnInit {
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  readonly sidebarService = inject(SidebarService);

  userRole: string = '';

  private _activeTooltip = signal<string | null>(null);
  get activeTooltip(): string | null {
    return this._activeTooltip();
  }
  set activeTooltip(value: string | null) {
    this._activeTooltip.set(value);
    this.cdr.markForCheck();
  }

  private _tooltipTop = signal<number>(0);
  get tooltipTop(): number {
    return this._tooltipTop();
  }
  set tooltipTop(value: number) {
    this._tooltipTop.set(value);
    this.cdr.markForCheck();
  }

  private _tooltipLeft = signal<number>(0);
  get tooltipLeft(): number {
    return this._tooltipLeft();
  }
  set tooltipLeft(value: number) {
    this._tooltipLeft.set(value);
    this.cdr.markForCheck();
  }

  get isCollapsed(): boolean {
    return this.sidebarService.isCollapsed();
  }

  get isMobileOpen(): boolean {
    return this.sidebarService.isMobileOpen();
  }

  constructor() {
    this.router.events
      .pipe(
        filter((event): event is NavigationStart => event instanceof NavigationStart),
        takeUntilDestroyed()
      )
      .subscribe(() => {
        this.activeTooltip = null;
        this.closeMobileMenu();
      });
  }

  ngOnInit() {
    if (typeof localStorage === 'undefined') return;
    const userDataStr = localStorage.getItem('user_data');
    if (userDataStr) {
      try {
        const user = JSON.parse(userDataStr);
        this.userRole = user.rol || '';
        this.cdr.markForCheck();
      } catch (e) {
        console.error('Error parseando usuario', e);
      }
    }
  }

  toggleSidebar(): void {
    this.activeTooltip = null;
    this.sidebarService.toggle();
    this.cdr.markForCheck();
  }

  onItemMouseEnter(event: MouseEvent | FocusEvent, title: string): void {
    if (!this.isCollapsed) {
      this.activeTooltip = null;
      return;
    }
    const target = (event.currentTarget || event.target) as HTMLElement | null;
    if (target && typeof target.getBoundingClientRect === 'function') {
      const rect = target.getBoundingClientRect();
      this.activeTooltip = title;
      this.tooltipTop = rect.top + rect.height / 2;
      this.tooltipLeft = rect.right + 10;
    }
  }

  onItemMouseLeave(): void {
    this.activeTooltip = null;
  }

  openMobileMenu(): void {
    this.sidebarService.openMobile();
    this.cdr.markForCheck();
  }

  closeMobileMenu(): void {
    this.sidebarService.closeMobile();
    this.cdr.markForCheck();
  }

  onNavClick(): void {
    this.closeMobileMenu();
  }

  @HostListener('document:keydown.escape')
  handleEscape(): void {
    this.activeTooltip = null;
    if (this.isMobileOpen) {
      this.closeMobileMenu();
    }
  }

  logout(): void {
    this.closeMobileMenu();
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
