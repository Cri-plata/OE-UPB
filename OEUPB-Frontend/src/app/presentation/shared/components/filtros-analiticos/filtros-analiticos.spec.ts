import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { FiltrosAnaliticos } from '../../../../data/api/reportes.api';
import { FiltrosAnaliticosComponent } from './filtros-analiticos';

describe('FiltrosAnaliticosComponent', () => {
  it('emite la selección múltiple ordenada y la limpia', async () => {
    TestBed.configureTestingModule({
      imports: [FiltrosAnaliticosComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });
    const fixture = TestBed.createComponent(FiltrosAnaliticosComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('http://localhost:8000/api/reportes/filtros').flush({ programas: ['Derecho', 'Medicina'], anios: [2023, 2024], momentos: [0, 1] });
    await fixture.whenStable();

    const emitidos: FiltrosAnaliticos[] = [];
    fixture.componentInstance.aplicar.subscribe(filtros => emitidos.push(filtros));
    const casillas = fixture.nativeElement.querySelectorAll('input[type=checkbox]') as NodeListOf<HTMLInputElement>;
    expect(casillas.length).toBe(4);
    [casillas[1], casillas[0], casillas[3]].forEach(casilla => { casilla.checked = true; casilla.dispatchEvent(new Event('change')); });

    fixture.componentInstance.emitir();
    expect(emitidos[0]).toEqual({ programas: ['Derecho', 'Medicina'], anios: [2024], momento: undefined });

    fixture.componentInstance.limpiar();
    expect(emitidos[1]).toEqual({ programas: [], anios: [], momento: undefined });
    http.verify();
  });
});
