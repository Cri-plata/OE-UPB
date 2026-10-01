import { TestBed, ComponentFixture } from '@angular/core/testing';
import { provideRouter, Router, NavigationStart } from '@angular/router';
import { SidebarComponent } from './sidebar';
import { SidebarService } from '../../services/sidebar.service';

describe('SidebarComponent', () => {
  let fixture: ComponentFixture<SidebarComponent>;
  let component: SidebarComponent;
  let sidebarService: SidebarService;
  let router: Router;

  beforeEach(async () => {
    localStorage.clear();
    document.body.classList.remove('sidebar-collapsed', 'mobile-nav-open');

    await TestBed.configureTestingModule({
      imports: [SidebarComponent],
      providers: [provideRouter([{ path: '**', component: class {} }])]
    }).compileComponents();

    sidebarService = TestBed.inject(SidebarService);
    router = TestBed.inject(Router);
    fixture = TestBed.createComponent(SidebarComponent);
    component = fixture.componentInstance;
  });

  afterEach(() => {
    localStorage.clear();
    document.body.classList.remove('sidebar-collapsed', 'mobile-nav-open');
  });

  describe('permisos por rol', () => {
    it('no muestra datos privados a Usuario_Consulta', () => {
      localStorage.setItem('user_data', JSON.stringify({ rol: 'Usuario_Consulta' }));
      component.ngOnInit();
      fixture.detectChanges();
      expect(fixture.nativeElement.textContent).not.toContain('Directorio');
      expect(fixture.nativeElement.textContent).toContain('Gráficas publicadas');
      expect(fixture.nativeElement.textContent).toContain('Mi Perfil');
    });

    it('muestra carga y directorio al coordinador', () => {
      localStorage.setItem('user_data', JSON.stringify({ rol: 'Coordinador_Sede' }));
      component.ngOnInit();
      fixture.detectChanges();
      expect(fixture.nativeElement.textContent).toContain('Directorio');
      expect(fixture.nativeElement.textContent).toContain('Cargar datos');
    });
  });

  describe('logo institucional', () => {
    it('renderiza la imagen escudo-upb.png con clase brand-logo en lugar de texto plano', () => {
      fixture.detectChanges();
      const brandMark = fixture.nativeElement.querySelector('.brand-mark');
      expect(brandMark).toBeTruthy();

      const logoImg: HTMLImageElement | null = brandMark.querySelector('img.brand-logo');
      expect(logoImg).toBeTruthy();
      expect(logoImg?.getAttribute('src')).toBe('escudo-upb.png');
      expect(logoImg?.getAttribute('alt')).toBe('Escudo UPB');
    });
  });

  describe('colapso y expansión', () => {
    it('alterna el estado de colapso mediante el botón toggle', () => {
      fixture.detectChanges();
      const toggleBtn: HTMLButtonElement = fixture.nativeElement.querySelector('.sidebar-toggle-btn');
      expect(toggleBtn).toBeTruthy();
      expect(component.isCollapsed).toBe(false);
      expect(toggleBtn.getAttribute('aria-expanded')).toBe('true');
      expect(toggleBtn.getAttribute('aria-label')).toBe('Contraer barra lateral');

      // Click para colapsar
      toggleBtn.click();
      fixture.detectChanges();

      expect(component.isCollapsed).toBe(true);
      expect(sidebarService.isCollapsed()).toBe(true);
      expect(document.body.classList.contains('sidebar-collapsed')).toBe(true);
      expect(toggleBtn.getAttribute('aria-expanded')).toBe('false');
      expect(toggleBtn.getAttribute('aria-label')).toBe('Expandir barra lateral');

      const aside: HTMLElement = fixture.nativeElement.querySelector('aside.sidebar');
      expect(aside.classList.contains('collapsed')).toBe(true);

      // Click para expandir nuevamente
      toggleBtn.click();
      fixture.detectChanges();

      expect(component.isCollapsed).toBe(false);
      expect(sidebarService.isCollapsed()).toBe(false);
      expect(document.body.classList.contains('sidebar-collapsed')).toBe(false);
      expect(toggleBtn.getAttribute('aria-expanded')).toBe('true');
      expect(aside.classList.contains('collapsed')).toBe(false);
    });

    it('sincroniza el estado cuando SidebarService cambia directamente', () => {
      fixture.detectChanges();
      expect(component.isCollapsed).toBe(false);

      sidebarService.setCollapsed(true);
      fixture.detectChanges();
      expect(component.isCollapsed).toBe(true);

      sidebarService.setCollapsed(false);
      fixture.detectChanges();
      expect(component.isCollapsed).toBe(false);
    });
  });

  describe('tooltips flotantes', () => {
    it('no activa tooltip al pasar el cursor si la barra está expandida', () => {
      sidebarService.setCollapsed(false);
      fixture.detectChanges();

      const navItem = fixture.nativeElement.querySelector('.nav-item');
      component.onItemMouseEnter({ currentTarget: navItem } as any, 'Mi Perfil');
      fixture.detectChanges();

      expect(component.activeTooltip).toBeNull();
      const tooltip = fixture.nativeElement.querySelector('.sidebar-floating-tooltip');
      expect(tooltip).toBeNull();
    });

    it('activa y posiciona el tooltip cuando la barra está colapsada y se pasa el cursor', () => {
      sidebarService.setCollapsed(true);
      fixture.detectChanges();

      const mockTarget = {
        getBoundingClientRect: () => ({
          top: 100,
          bottom: 140,
          left: 0,
          right: 72,
          width: 72,
          height: 40
        })
      } as unknown as HTMLElement;

      component.onItemMouseEnter({ currentTarget: mockTarget } as any, 'Mi Perfil');
      fixture.detectChanges();

      expect(component.activeTooltip).toBe('Mi Perfil');
      expect(component.tooltipTop).toBe(120); // 100 + 40/2
      expect(component.tooltipLeft).toBe(82); // 72 + 10

      const tooltip: HTMLElement | null = fixture.nativeElement.querySelector('.sidebar-floating-tooltip');
      expect(tooltip).toBeTruthy();
      expect(tooltip?.textContent?.trim()).toBe('Mi Perfil');
      expect(tooltip?.style.top).toBe('120px');
      expect(tooltip?.style.left).toBe('82px');

      // Ocultar al salir el cursor
      component.onItemMouseLeave();
      fixture.detectChanges();
      expect(component.activeTooltip).toBeNull();
      expect(fixture.nativeElement.querySelector('.sidebar-floating-tooltip')).toBeNull();
    });

    it('cierra el tooltip al presionar la tecla Escape', () => {
      sidebarService.setCollapsed(true);
      fixture.detectChanges();

      component.activeTooltip = 'Reporte general';
      fixture.detectChanges();
      expect(fixture.nativeElement.querySelector('.sidebar-floating-tooltip')).toBeTruthy();

      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
      fixture.detectChanges();

      expect(component.activeTooltip).toBeNull();
      expect(fixture.nativeElement.querySelector('.sidebar-floating-tooltip')).toBeNull();
    });

    it('limpia el tooltip al navegar de ruta', async () => {
      sidebarService.setCollapsed(true);
      fixture.detectChanges();

      component.activeTooltip = 'Tendencias';
      fixture.detectChanges();
      expect(component.activeTooltip).toBe('Tendencias');

      await router.navigateByUrl('/');
      fixture.detectChanges();

      expect(component.activeTooltip).toBeNull();
    });
  });

  describe('retención de estilo en ruta activa', () => {
    it('mantiene la clase active y conserva routerLinkActive en los enlaces', () => {
      localStorage.setItem('user_data', JSON.stringify({ rol: 'Coordinador_Sede' }));
      component.ngOnInit();
      fixture.detectChanges();

      const links: NodeListOf<HTMLAnchorElement> = fixture.nativeElement.querySelectorAll('.nav-menu a.nav-item');
      expect(links.length).toBeGreaterThan(0);

      links.forEach(link => {
        expect(link.getAttribute('routerLinkActive')).toBe('active');
      });

      // Simular enlace activo y verificar que conserva los estilos/clase
      const firstLink = links[0];
      firstLink.classList.add('active');
      expect(firstLink.classList.contains('active')).toBe(true);

      // Al colapsar, la clase active persiste
      sidebarService.setCollapsed(true);
      fixture.detectChanges();
      expect(firstLink.classList.contains('active')).toBe(true);
    });
  });

  describe('navegación móvil drawer', () => {
    it('renderiza la cabecera móvil y el botón hamburguesa con sus atributos', () => {
      fixture.detectChanges();
      const mobileHeader: HTMLElement = fixture.nativeElement.querySelector('.mobile-header');
      expect(mobileHeader).toBeTruthy();

      const brand = mobileHeader.querySelector('.mobile-brand');
      expect(brand).toBeTruthy();
      expect(brand?.textContent).toContain('OEUPB');

      const logo = brand?.querySelector('img.mobile-brand-logo');
      expect(logo).toBeTruthy();
      expect(logo?.getAttribute('src')).toBe('escudo-upb.png');
      expect(logo?.getAttribute('alt')).toBe('Escudo UPB');

      const toggleBtn: HTMLButtonElement = mobileHeader.querySelector('.menu-toggle-btn')!;
      expect(toggleBtn).toBeTruthy();
      expect(toggleBtn.getAttribute('aria-label')).toBe('Abrir menú de navegación');
      expect(toggleBtn.getAttribute('aria-expanded')).toBe('false');
      expect(toggleBtn.querySelector('.menu-icon')).toBeTruthy();
    });

    it('abre el menú móvil al hacer clic en el botón hamburguesa', () => {
      fixture.detectChanges();
      const toggleBtn: HTMLButtonElement = fixture.nativeElement.querySelector('.menu-toggle-btn');
      toggleBtn.click();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(true);
      expect(sidebarService.isMobileOpen()).toBe(true);
      expect(document.body.classList.contains('mobile-nav-open')).toBe(true);
      expect(toggleBtn.getAttribute('aria-expanded')).toBe('true');

      const aside: HTMLElement = fixture.nativeElement.querySelector('aside.sidebar');
      expect(aside.classList.contains('mobile-open')).toBe(true);
    });

    it('renderiza el backdrop cuando está abierto y cierra el menú al hacer clic en él', () => {
      fixture.detectChanges();
      expect(fixture.nativeElement.querySelector('.sidebar-backdrop')).toBeNull();

      sidebarService.openMobile();
      fixture.detectChanges();

      const backdrop: HTMLElement = fixture.nativeElement.querySelector('.sidebar-backdrop');
      expect(backdrop).toBeTruthy();

      backdrop.click();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(false);
      expect(sidebarService.isMobileOpen()).toBe(false);
      expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
      expect(fixture.nativeElement.querySelector('.sidebar-backdrop')).toBeNull();
    });

    it('cierra el menú móvil con el botón cerrar (X) dentro de la barra lateral', () => {
      sidebarService.openMobile();
      fixture.detectChanges();

      const closeBtn: HTMLButtonElement = fixture.nativeElement.querySelector('.sidebar-close-btn');
      expect(closeBtn).toBeTruthy();
      expect(closeBtn.querySelector('.close-icon')).toBeTruthy();

      closeBtn.click();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(false);
      expect(sidebarService.isMobileOpen()).toBe(false);
      expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
    });

    it('cierra el menú móvil al hacer clic en un enlace de navegación', () => {
      localStorage.setItem('user_data', JSON.stringify({ rol: 'Usuario_Consulta' }));
      component.ngOnInit();
      sidebarService.openMobile();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(true);

      const link: HTMLAnchorElement = fixture.nativeElement.querySelector('.nav-menu a.nav-item');
      expect(link).toBeTruthy();

      link.click();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(false);
      expect(sidebarService.isMobileOpen()).toBe(false);
      expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
    });

    it('cierra el menú móvil al hacer clic en el botón cerrar sesión', () => {
      sidebarService.openMobile();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(true);

      const logoutBtn: HTMLButtonElement = fixture.nativeElement.querySelector('.logout-btn');
      expect(logoutBtn).toBeTruthy();

      logoutBtn.click();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(false);
      expect(sidebarService.isMobileOpen()).toBe(false);
      expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
    });

    it('cierra el menú móvil al presionar la tecla Escape', () => {
      sidebarService.openMobile();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(true);

      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(false);
      expect(sidebarService.isMobileOpen()).toBe(false);
      expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
    });

    it('cierra el menú móvil al navegar de ruta', async () => {
      sidebarService.openMobile();
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(true);

      await router.navigateByUrl('/');
      fixture.detectChanges();

      expect(component.isMobileOpen).toBe(false);
      expect(sidebarService.isMobileOpen()).toBe(false);
      expect(document.body.classList.contains('mobile-nav-open')).toBe(false);
    });
  });
});
