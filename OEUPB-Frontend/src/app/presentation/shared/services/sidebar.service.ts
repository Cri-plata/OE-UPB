import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SidebarService {
  private static readonly STORAGE_KEY = 'oeupb_sidebar_collapsed';

  private _collapsed = signal<boolean>(false);
  readonly isCollapsed = this._collapsed.asReadonly();

  private _mobileOpen = signal<boolean>(false);
  readonly isMobileOpen = this._mobileOpen.asReadonly();

  constructor() {
    this.restorePreference();
  }

  private restorePreference(): void {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      try {
        const stored = localStorage.getItem(SidebarService.STORAGE_KEY);
        if (stored !== null) {
          const collapsed = stored === 'true';
          this._collapsed.set(collapsed);
          this.updateBodyClass(collapsed);
        }
      } catch (e) {
        console.error('Error reading sidebar preference from localStorage', e);
      }
    }
  }

  toggle(): void {
    this.setCollapsed(!this._collapsed());
  }

  setCollapsed(collapsed: boolean): void {
    this._collapsed.set(collapsed);
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(SidebarService.STORAGE_KEY, String(collapsed));
      } catch (e) {
        console.error('Error saving sidebar state to localStorage', e);
      }
    }
    this.updateBodyClass(collapsed);
  }

  openMobile(): void {
    this._mobileOpen.set(true);
    this.updateMobileBodyClass(true);
  }

  closeMobile(): void {
    this._mobileOpen.set(false);
    this.updateMobileBodyClass(false);
  }

  toggleMobile(): void {
    const next = !this._mobileOpen();
    this._mobileOpen.set(next);
    this.updateMobileBodyClass(next);
  }

  private updateBodyClass(collapsed: boolean): void {
    if (typeof document !== 'undefined' && document.body) {
      if (collapsed) {
        document.body.classList.add('sidebar-collapsed');
      } else {
        document.body.classList.remove('sidebar-collapsed');
      }
    }
  }

  private updateMobileBodyClass(open: boolean): void {
    if (typeof document !== 'undefined' && document.body) {
      if (open) {
        document.body.classList.add('mobile-nav-open');
      } else {
        document.body.classList.remove('mobile-nav-open');
      }
    }
  }
}
