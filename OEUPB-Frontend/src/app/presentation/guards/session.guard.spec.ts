import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, Router, UrlTree } from '@angular/router';
import { authGuard, guestGuard, rolesGuard } from './session.guard';

describe('guards de sesión y rol', () => {
  const router = { parseUrl: vi.fn((url: string) => ({ url }) as unknown as UrlTree) };

  beforeEach(() => {
    localStorage.clear();
    router.parseUrl.mockClear();
    TestBed.configureTestingModule({ providers: [{ provide: Router, useValue: router }] });
  });

  it('envía al login cuando no existe sesión', () => {
    const resultado = TestBed.runInInjectionContext(() => authGuard({} as ActivatedRouteSnapshot, {} as any));
    expect((resultado as any).url).toBe('/login');
  });

  it('deniega una ruta de coordinador a Usuario_Consulta', () => {
    localStorage.setItem('jwt_token', 'token');
    localStorage.setItem('user_data', JSON.stringify({ rol: 'Usuario_Consulta', debeCambiarContrasena: false }));
    const route = { data: { roles: ['Coordinador_Sede'] } } as unknown as ActivatedRouteSnapshot;
    const resultado = TestBed.runInInjectionContext(() => rolesGuard(route, {} as any));
    expect((resultado as any).url).toBe('/publicaciones');
  });

  it('evita volver al login con una sesión completa', () => {
    localStorage.setItem('jwt_token', 'token');
    localStorage.setItem('user_data', JSON.stringify({ rol: 'Admin_CTIC', debeCambiarContrasena: false }));
    const resultado = TestBed.runInInjectionContext(() => guestGuard({} as ActivatedRouteSnapshot, {} as any));
    expect((resultado as any).url).toBe('/admin-usuarios');
  });
});
