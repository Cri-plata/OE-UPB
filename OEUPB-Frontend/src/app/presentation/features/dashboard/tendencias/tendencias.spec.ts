import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { TendenciasComponent } from './tendencias';

const API = 'http://localhost:8000/api';

describe('TendenciasComponent', () => {
  let http: HttpTestingController;

  function crear() {
    TestBed.configureTestingModule({
      imports: [TendenciasComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
    });
    const fixture = TestBed.createComponent(TendenciasComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(`${API}/publicaciones/mias`).flush([]);
    http.expectOne(`${API}/reportes/filtros`).flush({ programas: ['Derecho'], anios: [2024], momentos: [0, 1] });
    http.expectOne(r => r.url === `${API}/reportes/tendencias`).flush({ labels: ['M0', 'M1', 'M5'], datasets: [] });
    return fixture;
  }

  afterEach(() => http.verify());

  it('compara dos momentos y aplica los filtros a ambas consultas', async () => {
    const fixture = crear();
    const comparacion = http.expectOne(r => r.url === `${API}/reportes/comparacion`);
    expect(comparacion.request.params.get('momento_inicial')).toBe('0');
    expect(comparacion.request.params.get('momento_final')).toBe('1');
    comparacion.flush({ momento_inicial: 0, momento_final: 1, indicador: 'empleabilidad', minimo_pares: 5, programas: [
      { programa: 'Derecho', pares: 6, suficiente: true, valor_inicial: 0, valor_final: 83.3 },
      { programa: 'Medicina', pares: 2, suficiente: false, valor_inicial: null, valor_final: null },
    ] });
    await fixture.whenStable();
    expect(fixture.componentInstance.comparacionChartData().labels).toEqual(['Derecho (6 pares)']);
    expect(fixture.nativeElement.textContent).toContain('Sin pares suficientes: Medicina (2)');

    fixture.componentInstance.aplicarFiltros({ programas: ['Derecho'], anios: [2024] });
    const tendencias = http.expectOne(r => r.url === `${API}/reportes/tendencias`);
    expect(tendencias.request.params.getAll('programas')).toEqual(['Derecho']);
    expect(tendencias.request.params.getAll('anios')).toEqual(['2024']);
    tendencias.flush({ labels: [], datasets: [] });
    const filtrada = http.expectOne(r => r.url === `${API}/reportes/comparacion`);
    expect(filtrada.request.params.getAll('programas')).toEqual(['Derecho']);
    filtrada.flush({ momento_inicial: 0, momento_final: 1, indicador: 'empleabilidad', minimo_pares: 5, programas: [] });
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Datos insuficientes para la comparación seleccionada');
  });

  it('rechaza comparar un momento consigo mismo sin consultar al backend', () => {
    const fixture = crear();
    http.expectOne(r => r.url === `${API}/reportes/comparacion`).flush({ momento_inicial: 0, momento_final: 1, indicador: 'empleabilidad', minimo_pares: 5, programas: [] });
    fixture.componentInstance.cambiarComparacion('final', '0');
    expect(fixture.componentInstance.errorComparacion()).toBe('Seleccione dos momentos distintos.');
  });
});
