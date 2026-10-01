import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';

import { PerfilEgresadoResponse } from '../../../../data/api/generated-api.models';
import { FichaEgresado } from './ficha-egresado';

const URL = 'http://localhost:8000/api/directorio/perfil/1000000001';

const perfil: PerfilEgresadoResponse = {
  documento: '1000000001',
  id_estudiante: '1234567',
  nombre_completo: 'Egresada Demo',
  programa: 'Derecho',
  fecha_grado: '2024-06-21',
  encuestas: [],
};

describe('FichaEgresado', () => {
  let http: HttpTestingController;

  async function crear(respuesta: PerfilEgresadoResponse) {
    TestBed.configureTestingModule({
      imports: [FichaEgresado],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap({ cedula: '1000000001' }) } } },
      ]
    });
    const fixture = TestBed.createComponent(FichaEgresado);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(URL).flush(respuesta);
    await fixture.whenStable();
    return fixture.nativeElement as HTMLElement;
  }

  afterEach(() => http.verify());

  it('muestra el ID del estudiante debajo de la cédula', async () => {
    const elemento = await crear(perfil);
    const lineas = Array.from(elemento.querySelectorAll('.identificacion p')).map(p => p.textContent?.trim());
    expect(lineas).toEqual(['C.C. 1000000001', 'ID 1234567']);
  });

  it('omite la línea del ID cuando el egresado no lo tiene', async () => {
    const elemento = await crear({ ...perfil, id_estudiante: null });
    const lineas = Array.from(elemento.querySelectorAll('.identificacion p')).map(p => p.textContent?.trim());
    expect(lineas).toEqual(['C.C. 1000000001']);
  });
});
