import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { PublicacionResponse } from '../../../../data/api/generated-api.models';
import { PublicacionesComponent } from './publicaciones';

const URL = 'http://localhost:8000/api/publicaciones/';

const publicacion = {
  id: 1,
  grafica_key: 'reporte_general_distribucion_programas',
  titulo: 'Distribución por programa',
  sede_id: 2,
  sede_nombre: 'Medellín',
  programas: ['Derecho'],
  permiso_requerido: 'ver_reporte_general',
  definicion: { origen: 'reporte_general', tipo_visualizacion: 'bar', indicador: 'distribucion_programas' },
  metricas: { labels: ['Derecho'], datasets: [{ label: 'Egresados', data: [6] }] },
  version: 1,
  estado: 'publicada',
  aprobada_privacidad: true,
  fecha_publicacion: '2026-09-25T10:00:00',
  fecha_retiro: null,
} as PublicacionResponse;

describe('PublicacionesComponent', () => {
  let http: HttpTestingController;

  async function crear() {
    TestBed.configureTestingModule({
      imports: [PublicacionesComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
    });
    const fixture = TestBed.createComponent(PublicacionesComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    return fixture;
  }

  // Sin detectChanges manual: la vista debe refrescarse sola (aplicación zoneless).
  async function texto(fixture: Awaited<ReturnType<typeof crear>>) {
    await fixture.whenStable();
    return (fixture.nativeElement as HTMLElement).textContent ?? '';
  }

  afterEach(() => http.verify());

  it('termina la carga y presenta el catálogo recibido', async () => {
    const fixture = await crear();
    expect(await texto(fixture)).toContain('Cargando publicaciones');
    http.expectOne(URL).flush([publicacion]);

    const contenido = await texto(fixture);
    expect(fixture.componentInstance.cargando()).toBe(false);
    expect(contenido).not.toContain('Cargando publicaciones');
    expect(contenido).toContain('Distribución por programa');
    expect(contenido).toContain('Medellín');
  });

  it('muestra el estado vacío cuando no hay publicaciones compatibles', async () => {
    const fixture = await crear();
    http.expectOne(URL).flush([]);
    const contenido = await texto(fixture);
    expect(contenido).toContain('No hay gráficas publicadas compatibles');
    expect(contenido).not.toContain('Cargando publicaciones');
  });

  it('muestra el error y permite reintentar hasta obtener el catálogo', async () => {
    const fixture = await crear();
    http.expectOne(URL).error(new ProgressEvent('error'), { status: 0 });
    expect(await texto(fixture)).toContain('No hay conexión con el servidor');

    const reintentar = Array.from((fixture.nativeElement as HTMLElement).querySelectorAll('button'))
      .find(boton => boton.textContent?.includes('Reintentar'));
    expect(reintentar).toBeDefined();
    reintentar!.click();
    http.expectOne(URL).flush([publicacion]);

    const contenido = await texto(fixture);
    expect(contenido).toContain('Distribución por programa');
    expect(fixture.componentInstance.error()).toBe('');
  });
});
