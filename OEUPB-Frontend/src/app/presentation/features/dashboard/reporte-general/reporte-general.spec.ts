import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { KpisResponse } from '../../../../data/api/generated-api.models';
import { ReporteGeneralComponent } from './reporte-general';

const API = 'http://localhost:8000/api';
const kpis: KpisResponse = {
  total_egresados: 8, total_encuestados: 14, tasa_empleabilidad: 50, tasa_formalidad: 80, tasa_informalidad: 20,
  observaciones_formalidad: 5, promedio_salarial: 2.5, rango_salarial: { minimo: 2.5, mediana: 2.5, maximo: 2.5, observaciones: 2 },
  distribucion_estado_laboral: { empleado: 6, independiente: 1, estudiante: 6, sin_empleo: 1 },
  distribucion_programas: { Derecho: 6, Medicina: 2 }, nivel_satisfaccion: {},
};

describe('ReporteGeneralComponent', () => {
  let http: HttpTestingController;

  afterEach(() => http.verify());

  it('muestra formalidad y rango salarial, y publica con los filtros vigentes', async () => {
    TestBed.configureTestingModule({
      imports: [ReporteGeneralComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
    });
    const fixture = TestBed.createComponent(ReporteGeneralComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(`${API}/publicaciones/mias`).flush([]);
    http.expectOne(`${API}/reportes/filtros`).flush({ programas: ['Derecho', 'Medicina'], anios: [2024], momentos: [0, 1] });
    http.expectOne(r => r.url === `${API}/reportes/general`).flush(kpis);
    await fixture.whenStable();

    const texto = fixture.nativeElement.textContent as string;
    expect(texto).toContain('80%');
    expect(texto).toContain('Informal 20%');
    expect(texto).toContain('Rango 2.5–2.5');

    const componente = fixture.componentInstance;
    componente.aplicarFiltros({ programas: ['Derecho'], anios: [2024], momento: 1 });
    const filtrado = http.expectOne(r => r.url === `${API}/reportes/general`);
    expect(filtrado.request.params.getAll('programas')).toEqual(['Derecho']);
    expect(filtrado.request.params.get('momento')).toBe('1');
    filtrado.flush(kpis);

    vi.spyOn(window, 'confirm').mockReturnValue(true);
    componente.publicar('reporte_general_estado_laboral', 'Estado Laboral', 'estado_laboral', 'bar');
    const publicacion = http.expectOne(`${API}/publicaciones/`);
    expect(publicacion.request.body.grafica_key).toMatch(/^reporte_general_estado_laboral_[a-z0-9]+$/);
    expect(publicacion.request.body.definicion).toEqual({
      origen: 'reporte_general', tipo_visualizacion: 'bar', indicador: 'estado_laboral', programas: ['Derecho'], anios: [2024], momento: 1,
    });
    expect(publicacion.request.body.titulo).toContain('Derecho');
    publicacion.flush({ id: 1, grafica_key: publicacion.request.body.grafica_key, version: 1 });
  });
});
