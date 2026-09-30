import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { HabilidadesDemandadasComponent } from './habilidades-demandadas';
import { CHART_PALETTE } from '../../../shared/chart-palette';

const API = 'http://localhost:8000/api';

const HABILIDADES_RESPONSE = {
  habilidades_reconocidas: [
    { habilidad: 'Liderazgo', tipo: 'blanda', menciones: 5 },
    { habilidad: 'Comunicación', tipo: 'blanda', menciones: 4 },
    { habilidad: 'Análisis de datos', tipo: 'dura', menciones: 3 },
    { habilidad: 'Inglés / Segundo idioma', tipo: 'dura', menciones: 2 },
  ],
  candidatas_emergentes: [
    { termino: 'kubernetes', score_tfidf: 0.72, frecuencia_documentos: 3 },
  ],
  estadisticas: {
    total_respuestas_analizadas: 20,
    respuestas_con_habilidad: 18,
    respuestas_sin_habilidad: 2,
  },
};

const REGLAS_RESPONSE = {
  total_respuestas: 20,
  transacciones_validas: 15,
  transacciones_insuficientes: 5,
  total_reglas: 2,
  reglas: [
    { si_menciona: 'Liderazgo', tambien_menciona: 'Comunicación', ocurrencias: 4, soporte: 0.2667, confianza: 0.8, lift: 3.0 },
    { si_menciona: 'Análisis de datos', tambien_menciona: 'Inglés / Segundo idioma', ocurrencias: 2, soporte: 0.1333, confianza: 0.667, lift: 5.0 },
  ],
};

const PROGRAMAS_RESPONSE = ['Derecho', 'Ingeniería de Sistemas', 'Medicina'];

describe('HabilidadesDemandadasComponent', () => {
  let http: HttpTestingController;

  function crear() {
    TestBed.configureTestingModule({
      imports: [HabilidadesDemandadasComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])]
    });
    const fixture = TestBed.createComponent(HabilidadesDemandadasComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();

    // El componente dispara 3 peticiones en ngOnInit: programas, habilidades y reglas
    http.expectOne(`${API}/directorio/programas`).flush(PROGRAMAS_RESPONSE);
    http.expectOne(r => r.url === `${API}/ia/habilidades-demandadas`).flush(HABILIDADES_RESPONSE);
    http.expectOne(r => r.url === `${API}/ia/reglas-asociacion`).flush(REGLAS_RESPONSE);
    fixture.detectChanges();
    return fixture;
  }

  afterEach(() => http.verify());

  it('se crea correctamente y carga datos iniciales', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp).toBeTruthy();
    expect(comp.habilidadesReconocidas.length).toBe(4);
    expect(comp.candidatasEmergentes.length).toBe(1);
    expect(comp.reglasAsociacion.length).toBe(2);
    expect(comp.estadisticas?.total_respuestas_analizadas).toBe(20);
    expect(comp.totalRespuestasReglas).toBe(20);
    expect(comp.transaccionesValidas).toBe(15);
  });

  it('separa habilidades blandas y duras en los gráficos', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.blandasChartData.labels).toEqual(['Liderazgo', 'Comunicación']);
    expect(comp.blandasChartData.datasets[0].data).toEqual([5, 4]);
    expect(comp.durasChartData.labels).toEqual(['Análisis de datos', 'Inglés / Segundo idioma']);
    expect(comp.durasChartData.datasets[0].data).toEqual([3, 2]);
    expect(comp.isChartReady).toBe(true);
  });

  it('usa colores del CHART_PALETTE y no hex crudos', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    // Los colores deben provenir de CHART_PALETTE, no ser hex arbitrarios
    const bgBlandas = comp.blandasChartData.datasets[0].backgroundColor as string;
    const bgDuras = comp.durasChartData.datasets[0].backgroundColor as string;
    expect(bgBlandas).toBe(CHART_PALETTE[2]);
    expect(bgDuras).toBe(CHART_PALETTE[0]);
  });

  it('clasifica el Lift correctamente', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.getLiftBadge(5.0)).toBe('badge-alto');
    expect(comp.getLiftBadge(3.0)).toBe('badge-medio');
    expect(comp.getLiftBadge(1.2)).toBe('badge-base');

    expect(comp.getLiftTexto(5.0)).toBe('Muy Fuerte');
    expect(comp.getLiftTexto(3.0)).toBe('Significativo');
    expect(comp.getLiftTexto(1.2)).toBe('Moderado');
  });

  it('genera un insight interpretativo correcto', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;
    const regla = REGLAS_RESPONSE.reglas[0];
    const insight = comp.getInsight(regla);

    expect(insight).toContain('80%');
    expect(insight).toContain('Liderazgo');
    expect(insight).toContain('Comunicación');
  });

  it('aplica filtros y vuelve a consultar ambos endpoints', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    comp.filtroMomento = '1';
    comp.filtroPrograma = 'Derecho';
    comp.aplicarFiltros();

    const habsReq = http.expectOne(r => r.url === `${API}/ia/habilidades-demandadas`);
    expect(habsReq.request.params.get('momento')).toBe('1');
    expect(habsReq.request.params.get('programa')).toBe('Derecho');
    habsReq.flush(HABILIDADES_RESPONSE);

    const reglasReq = http.expectOne(r => r.url === `${API}/ia/reglas-asociacion`);
    expect(reglasReq.request.params.get('momento')).toBe('1');
    expect(reglasReq.request.params.get('programa')).toBe('Derecho');
    reglasReq.flush(REGLAS_RESPONSE);
  });

  it('carga la lista de programas disponibles para el filtro', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.programasDisponibles).toEqual(['Derecho', 'Ingeniería de Sistemas', 'Medicina']);
  });

  it('no tiene emojis en el template renderizado', () => {
    const fixture = crear();
    const html = fixture.nativeElement.innerHTML;
    // Rango Unicode de emojis comunes
    const emojiPattern = /[\u{1F300}-\u{1F9FF}]/u;
    expect(emojiPattern.test(html)).toBe(false);
  });

  it('muestra las reglas de asociación en la pestaña activa por defecto', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;
    expect(comp.activeTab).toBe('reglas');

    const table = fixture.nativeElement.querySelector('.data-table');
    expect(table).toBeTruthy();
    const rows = fixture.nativeElement.querySelectorAll('.data-table tbody tr');
    expect(rows.length).toBe(2);
  });

  it('cambia a la pestaña de habilidades correctamente', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.activeTab).toBe('reglas');
    comp.setTab('habilidades');
    expect(comp.activeTab).toBe('habilidades');
    comp.setTab('reglas');
    expect(comp.activeTab).toBe('reglas');
  });

  it('llama a exportarGrafica sin lanzar errores', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(() => comp.exportarGrafica('#grafica-habilidades-blandas canvas', 'test-blandas.png')).not.toThrow();
    expect(() => comp.exportarGrafica('#grafica-habilidades-duras canvas', 'test-duras.png')).not.toThrow();
  });

  it('incluye botones de exportación PNG para los gráficos de habilidades', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;
    comp.setTab('habilidades');
    fixture.detectChanges();

    // Verificar que los botones con texto PNG están en el template
    const botones = Array.from(fixture.nativeElement.querySelectorAll('button')) as HTMLButtonElement[];
    const btnPng = botones.filter(b => b.textContent?.trim() === 'PNG');
    expect(btnPng.length).toBe(2);
  });
});
