import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { PublicacionesApi } from './publicaciones.api';


describe('PublicacionesApi', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [provideHttpClient(), provideHttpClientTesting()]
  }));

  it('consulta únicamente el catálogo autorizado del backend', () => {
    const api = TestBed.inject(PublicacionesApi);
    const http = TestBed.inject(HttpTestingController);
    api.listarAutorizadas().subscribe(publicaciones => expect(publicaciones).toEqual([]));
    const req = http.expectOne('http://localhost:8000/api/publicaciones/');
    expect(req.request.method).toBe('GET');
    req.flush([]);
    http.verify();
  });
});
