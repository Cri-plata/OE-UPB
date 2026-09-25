import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { ExploradorComponent } from './explorador';

const API = 'http://localhost:8000/api';
const opciones = { preguntas: ['¿Trabaja?', '¿Estudia?'], programas: ['Derecho'], anios: [2024] };

describe('ExploradorComponent', () => {
  let http: HttpTestingController;

  function crear() {
    TestBed.configureTestingModule({
      imports: [ExploradorComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
    });
    const fixture = TestBed.createComponent(ExploradorComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(`${API}/publicaciones/mias`).flush([]);
    http.expectOne(`${API}/reportes/explorador/init`).flush(opciones);
    return fixture;
  }

  function responderExplorar(valores: number[]) {
    const req = http.expectOne(r => r.url === `${API}/reportes/explorador`);
    req.flush({ labels: valores.map((_, i) => `R${i}`), valores });
    return req.request.params;
  }

  afterEach(() => http.verify());

  it('mantiene varias gráficas simultáneas con estado independiente', async () => {
    const fixture = crear();
    await fixture.whenStable();
    responderExplorar([6, 1]);

    fixture.componentInstance.crearOtra();
    await fixture.whenStable();
    const segunda = responderExplorar([3]);
    expect(segunda.get('pregunta')).toBe('¿Trabaja?');
    expect(fixture.nativeElement.querySelectorAll('app-explorador-grafica').length).toBe(2);

    // Cambiar la segunda gráfica no vuelve a consultar ni altera la primera.
    const selects = fixture.nativeElement.querySelectorAll('app-explorador-grafica select');
    const preguntaSegunda = selects[5] as HTMLSelectElement;
    preguntaSegunda.value = '¿Estudia?';
    preguntaSegunda.dispatchEvent(new Event('change'));
    const params = responderExplorar([9]);
    expect(params.get('pregunta')).toBe('¿Estudia?');
    await fixture.whenStable();
    const titulos = Array.from(fixture.nativeElement.querySelectorAll('app-explorador-grafica h2')).map(h => (h as HTMLElement).textContent);
    expect(titulos).toEqual(['Gráfica 1: ¿Trabaja?', 'Gráfica 2: ¿Estudia?']);

    fixture.componentInstance.quitar(1);
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelectorAll('app-explorador-grafica').length).toBe(1);
    fixture.componentInstance.quitar(2);
    expect(fixture.componentInstance.bloques().length).toBe(1);
  });

  it('muestra el error de un bloque sin afectar a los demás', async () => {
    const fixture = crear();
    await fixture.whenStable();
    responderExplorar([6]);
    fixture.componentInstance.crearOtra();
    await fixture.whenStable();
    http.expectOne(r => r.url === `${API}/reportes/explorador`).flush({ detail: 'Variable no autorizada' }, { status: 422, statusText: 'Unprocessable Entity' });
    await fixture.whenStable();

    const bloques = fixture.nativeElement.querySelectorAll('app-explorador-grafica');
    expect(bloques[0].textContent).not.toContain('Variable no autorizada');
    expect(bloques[1].textContent).toContain('Variable no autorizada');
  });
});
