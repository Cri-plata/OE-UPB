import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { PublicacionResponse } from '../../../../data/api/generated-api.models';
import { AuthRepository } from '../../../../domain/repositories/auth.repository';
import { Usuario } from '../../../../domain/models/usuario.model';
import { PublicacionesComponent } from './publicaciones';

const URL = 'http://localhost:8000/api/publicaciones/';
const URL_MIAS = `${URL}mias`;

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

const propia = {
  ...publicacion,
  id: 10,
  grafica_key: 'reporte_general_estado_laboral',
  titulo: 'Estado laboral propio',
  sede_id: 1,
  sede_nombre: 'Bucaramanga',
} as PublicacionResponse;

function usuario(rol: Usuario['rol']): Usuario {
  return { id: 1, nombre: 'Demo', correo: 'demo@upb.edu.co', rol, sedeId: 1, debeCambiarContrasena: false };
}

describe('PublicacionesComponent', () => {
  let http: HttpTestingController;

  async function crear(rol: Usuario['rol'] = 'Usuario_Consulta') {
    TestBed.configureTestingModule({
      imports: [PublicacionesComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: AuthRepository, useValue: { getUsuarioActual: () => usuario(rol) } },
      ]
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

  function boton(fixture: Awaited<ReturnType<typeof crear>>, etiqueta: string) {
    return Array.from((fixture.nativeElement as HTMLElement).querySelectorAll('button'))
      .find(b => b.textContent?.includes(etiqueta));
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
    expect(contenido).not.toContain('Mis publicaciones');
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

    const reintentar = boton(fixture, 'Reintentar');
    expect(reintentar).toBeDefined();
    reintentar!.click();
    http.expectOne(URL).flush([publicacion]);

    const contenido = await texto(fixture);
    expect(contenido).toContain('Distribución por programa');
    expect(fixture.componentInstance.error()).toBe('');
  });

  it('al coordinador le muestra sus publicaciones y, aparte, las de los demás coordinadores', async () => {
    const fixture = await crear('Coordinador_Sede');
    http.expectOne(URL_MIAS).flush([propia]);
    http.expectOne(URL).flush([publicacion]);

    await fixture.whenStable();
    const secciones = Array.from((fixture.nativeElement as HTMLElement).querySelectorAll('section[aria-labelledby]'));
    const [mias, otras] = secciones.map(seccion => seccion.textContent ?? '');
    expect(mias).toContain('Mis publicaciones');
    expect(mias).toContain('Estado laboral propio');
    expect(mias).toContain('Retirar publicación');
    expect(otras).toContain('Publicadas por otros coordinadores');
    expect(otras).toContain('Distribución por programa');
    expect(otras).not.toContain('Retirar publicación');
  });

  it('el coordinador retira una publicación propia y la vista se actualiza sola', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    const fixture = await crear('Coordinador_Sede');
    http.expectOne(URL_MIAS).flush([propia]);
    http.expectOne(URL).flush([]);
    await texto(fixture);

    boton(fixture, 'Retirar publicación')!.click();
    expect(await texto(fixture)).toContain('Retirando…');
    const retiro = http.expectOne(`${URL}${propia.id}`);
    expect(retiro.request.method).toBe('DELETE');
    retiro.flush({ ...propia, estado: 'retirada' });

    const contenido = await texto(fixture);
    expect(contenido).not.toContain('Estado laboral propio');
    expect(contenido).toContain('Aún no has publicado gráficas');
    expect(contenido).toContain('No hay gráficas publicadas por otros coordinadores');
  });

  it('muestra el error del retiro bajo la tarjeta y conserva la publicación', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    const fixture = await crear('Coordinador_Sede');
    http.expectOne(URL_MIAS).flush([propia]);
    http.expectOne(URL).flush([]);
    await texto(fixture);

    boton(fixture, 'Retirar publicación')!.click();
    http.expectOne(`${URL}${propia.id}`).error(new ProgressEvent('error'), { status: 0 });

    const contenido = await texto(fixture);
    expect(contenido).toContain('Estado laboral propio');
    expect(contenido).toContain('No hay conexión con el servidor');
    expect(boton(fixture, 'Retirar publicación')).toBeDefined();
  });
});
