import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { PublicacionCreate, PublicacionResponse } from '../../data/api/generated-api.models';
import { PublicacionControl } from './publicacion-control';

const URL = 'http://localhost:8000/api/publicaciones/';
const KEY = 'tendencias_empleabilidad';

const payload: PublicacionCreate = {
  grafica_key: KEY,
  titulo: 'Evolución histórica',
  definicion: { origen: 'tendencias', tipo_visualizacion: 'line', indicador: 'empleabilidad' },
  aprobada_privacidad: true,
};

const respuesta = { id: 7, grafica_key: KEY, version: 1, estado: 'publicada' } as PublicacionResponse;

describe('PublicacionControl', () => {
  let control: PublicacionControl;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [PublicacionControl, provideHttpClient(), provideHttpClientTesting()]
    });
    control = TestBed.inject(PublicacionControl);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('publica una sola vez y refleja el estado en cuanto responde el backend', () => {
    control.publicar(KEY, payload);
    control.publicar(KEY, payload);
    expect(control.procesando(KEY)).toBe(true);

    const req = http.expectOne(URL);
    expect(req.request.method).toBe('POST');
    req.flush(respuesta);

    expect(control.ocupado()).toBe(false);
    expect(control.estaPublicada(KEY)).toBe(true);
    expect(control.publicacion(KEY)?.version).toBe(1);
    expect(control.error(KEY)).toBe('');
  });

  it('termina la carga ante un error HTTP, muestra el motivo y permite reintentar', () => {
    control.publicar(KEY, payload);
    http.expectOne(URL).flush(
      { detail: 'No hay celdas con al menos 5 observaciones para publicar esta gráfica' },
      { status: 422, statusText: 'Unprocessable Entity' }
    );

    expect(control.ocupado()).toBe(false);
    expect(control.estaPublicada(KEY)).toBe(false);
    expect(control.error(KEY)).toContain('al menos 5 observaciones');

    control.publicar(KEY, payload);
    expect(control.error(KEY)).toBe('');
    http.expectOne(URL).flush(respuesta);
    expect(control.estaPublicada(KEY)).toBe(true);
  });

  it('termina la carga ante un error de red con un mensaje accionable', () => {
    control.publicar(KEY, payload);
    http.expectOne(URL).error(new ProgressEvent('error'), { status: 0 });

    expect(control.ocupado()).toBe(false);
    expect(control.error(KEY)).toContain('No hay conexión con el servidor');
  });

  it('retira y reconcilia una publicación que ya no estaba activa', () => {
    control.cargarPropias();
    http.expectOne(`${URL}mias`).flush([respuesta, { ...respuesta, id: 8, grafica_key: 'otra' }]);
    expect(control.estaPublicada(KEY)).toBe(true);

    control.retirar(KEY);
    http.expectOne(`${URL}7`).flush({ detail: 'La publicación ya no está activa' }, { status: 409, statusText: 'Conflict' });
    expect(control.estaPublicada(KEY)).toBe(false);
    expect(control.estaPublicada('otra')).toBe(true);

    control.retirar('otra');
    const retiro = http.expectOne(`${URL}8`);
    expect(retiro.request.method).toBe('DELETE');
    retiro.flush({ ...respuesta, id: 8, estado: 'retirada' });
    expect(control.estaPublicada('otra')).toBe(false);
    expect(control.ocupado()).toBe(false);
  });

  it('informa cuando no puede consultar el estado de publicación', () => {
    control.cargarPropias();
    http.expectOne(`${URL}mias`).flush({ detail: 'Error interno' }, { status: 500, statusText: 'Server Error' });
    expect(control.errorCarga()).toBe('Error interno');
  });
});
