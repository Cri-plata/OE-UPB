import { TestBed } from '@angular/core/testing';
import { SidebarService } from './sidebar.service';

describe('SidebarService', () => {
  let service: SidebarService;

  beforeEach(() => {
    localStorage.clear();
    document.body.classList.remove('sidebar-collapsed', 'mobile-nav-open');
    TestBed.configureTestingModule({});
    service = TestBed.inject(SidebarService);
  });

  afterEach(() => {
    localStorage.clear();
    document.body.classList.remove('sidebar-collapsed', 'mobile-nav-open');
  });

  it('debe inicializarse en false por defecto', () => {
    expect(service.isCollapsed()).toBe(false);
    expect(document.body.classList.contains('sidebar-collapsed')).toBe(false);
    expect(service.isMobileOpen()).toBe(false);
    expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
  });

  it('debe alternar el estado con toggle()', () => {
    service.toggle();
    expect(service.isCollapsed()).toBe(true);
    expect(document.body.classList.contains('sidebar-collapsed')).toBe(true);
    expect(localStorage.getItem('oeupb_sidebar_collapsed')).toBe('true');

    service.toggle();
    expect(service.isCollapsed()).toBe(false);
    expect(document.body.classList.contains('sidebar-collapsed')).toBe(false);
    expect(localStorage.getItem('oeupb_sidebar_collapsed')).toBe('false');
  });

  it('debe establecer el estado con setCollapsed()', () => {
    service.setCollapsed(true);
    expect(service.isCollapsed()).toBe(true);
    expect(document.body.classList.contains('sidebar-collapsed')).toBe(true);

    service.setCollapsed(false);
    expect(service.isCollapsed()).toBe(false);
    expect(document.body.classList.contains('sidebar-collapsed')).toBe(false);
  });

  it('debe restaurar la preferencia desde localStorage al instanciarse', () => {
    localStorage.setItem('oeupb_sidebar_collapsed', 'true');
    const newService = new SidebarService();
    expect(newService.isCollapsed()).toBe(true);
    expect(document.body.classList.contains('sidebar-collapsed')).toBe(true);
  });

  it('debe abrir el menú móvil con openMobile() y agregar clase mobile-nav-open', () => {
    service.openMobile();
    expect(service.isMobileOpen()).toBe(true);
    expect(document.body.classList.contains('mobile-nav-open')).toBe(true);
  });

  it('debe cerrar el menú móvil con closeMobile() y quitar clase mobile-nav-open', () => {
    service.openMobile();
    expect(service.isMobileOpen()).toBe(true);
    expect(document.body.classList.contains('mobile-nav-open')).toBe(true);

    service.closeMobile();
    expect(service.isMobileOpen()).toBe(false);
    expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
  });

  it('debe alternar el menú móvil con toggleMobile()', () => {
    service.toggleMobile();
    expect(service.isMobileOpen()).toBe(true);
    expect(document.body.classList.contains('mobile-nav-open')).toBe(true);

    service.toggleMobile();
    expect(service.isMobileOpen()).toBe(false);
    expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
  });
});
