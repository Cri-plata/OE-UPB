import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { SidebarComponent } from './sidebar';

describe('SidebarComponent permisos', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ imports: [SidebarComponent], providers: [provideRouter([])] });
  });

  it('no muestra datos privados a Usuario_Consulta', () => {
    localStorage.setItem('user_data', JSON.stringify({ rol: 'Usuario_Consulta' }));
    const fixture = TestBed.createComponent(SidebarComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).not.toContain('Directorio');
    expect(fixture.nativeElement.textContent).toContain('Gráficas publicadas');
    expect(fixture.nativeElement.textContent).toContain('Mi Perfil');
  });

  it('muestra carga y directorio al coordinador', () => {
    localStorage.setItem('user_data', JSON.stringify({ rol: 'Coordinador_Sede' }));
    const fixture = TestBed.createComponent(SidebarComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Directorio');
    expect(fixture.nativeElement.textContent).toContain('Cargar datos');
  });
});
