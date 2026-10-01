import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { DirectorioComponent } from './directorio';

const TABLA = 'http://localhost:8000/api/directorio/tabla';
const fila = { documento: '1000000001', nombre_completo: 'Egresada Demo', programa: 'Derecho', fecha_grado: '2024-06-21', encuestas: 'M0 (2024)' };

describe('DirectorioComponent', () => {
  function crear() {
    TestBed.configureTestingModule({
      imports: [DirectorioComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
    });
    const fixture = TestBed.createComponent(DirectorioComponent);
    fixture.detectChanges();
    return { fixture, http: TestBed.inject(HttpTestingController) };
  }

  it('carga programas y tabla sin aceptar una sede del cliente', () => {
    const { fixture, http } = crear();
    http.expectOne('http://localhost:8000/api/directorio/programas').flush(['Derecho']);
    const tabla = http.expectOne(`${TABLA}?page=1&limit=50`);
    expect(tabla.request.params.has('sede_id')).toBe(false);
    tabla.flush({ total: 0, page: 1, limit: 50, data: [] });
    expect(fixture.componentInstance.programasDisponibles()).toEqual(['Derecho']);
    http.verify();
  });

  // Sin detectChanges manual: la tabla debe refrescarse sola (aplicación zoneless).
  it('muestra el resultado de la búsqueda en cuanto responde el backend', async () => {
    const { fixture, http } = crear();
    http.expectOne('http://localhost:8000/api/directorio/programas').flush([]);
    http.expectOne(`${TABLA}?page=1&limit=50`).flush({ total: 2, page: 1, limit: 50, data: [fila, { ...fila, documento: '1000000002' }] });
    await fixture.whenStable();

    fixture.componentInstance.terminoBusqueda = '000123456';
    fixture.componentInstance.onFiltroChange();
    http.expectOne(`${TABLA}?page=1&limit=50&q=000123456`).flush({ total: 1, page: 1, limit: 50, data: [fila] });
    await fixture.whenStable();

    const filas = (fixture.nativeElement as HTMLElement).querySelectorAll('tbody tr.clickable-row');
    expect(filas.length).toBe(1);
    expect(filas[0].textContent).toContain('1000000001');
    http.verify();
  });
});
