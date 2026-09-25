import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { DirectorioComponent } from './directorio';

describe('DirectorioComponent', () => {
  it('carga programas y tabla sin aceptar una sede del cliente', () => {
    TestBed.configureTestingModule({
      imports: [DirectorioComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
    });
    const fixture = TestBed.createComponent(DirectorioComponent);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('http://localhost:8000/api/directorio/programas').flush(['Derecho']);
    const tabla = http.expectOne('http://localhost:8000/api/directorio/tabla?page=1&limit=50');
    expect(tabla.request.params.has('sede_id')).toBe(false);
    tabla.flush({ total: 0, page: 1, limit: 50, data: [] });
    expect(fixture.componentInstance.programasDisponibles).toEqual(['Derecho']);
    http.verify();
  });
});
