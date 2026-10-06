import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { PerfilUsuarioComponent } from './perfil-usuario';

const API = 'http://localhost:8000/api';

describe('PerfilUsuarioComponent', () => {
  let http: HttpTestingController;

  function crear(usuario: object) {
    localStorage.setItem('user_data', JSON.stringify(usuario));
    TestBed.configureTestingModule({
      imports: [PerfilUsuarioComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    const fixture = TestBed.createComponent(PerfilUsuarioComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    return fixture;
  }

  afterEach(() => {
    http.verify();
    localStorage.clear();
  });

  it('muestra el nombre de la sede cuando llega la respuesta del catálogo', async () => {
    const fixture = crear({ id: 5, nombre: 'Profesor', correo: 'p@upb.edu.co', rol: 'Usuario_Consulta', sedeId: 1 });
    http.expectOne(`${API}/sedes/`).flush([{ id: 1, codigo: 'BUC', nombre: 'Bucaramanga' }]);
    // Zoneless: la vista solo se actualiza si el estado asíncrono vive en un signal.
    await fixture.whenStable();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Bucaramanga');
    expect((fixture.nativeElement as HTMLElement).textContent).not.toContain('Sin Sede Asignada');
  });

  it('indica alcance nacional para la cuenta CTIC sin sede', async () => {
    const fixture = crear({ id: 1, nombre: 'CTIC', correo: 'admin@upb.edu.co', rol: 'Admin_CTIC', sedeId: null });
    await fixture.whenStable();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Nivel Nacional');
  });
});
