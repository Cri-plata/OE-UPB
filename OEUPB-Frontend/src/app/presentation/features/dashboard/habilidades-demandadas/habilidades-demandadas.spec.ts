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

const COMPARATIVA_RESPONSE = {
  comparativa: [
    {
      habilidad: 'Gestión de proyectos',
      tipo: 'dura',
      total_menciones: 10,
      m0_menciones: 2,
      m0_porcentaje: 20.0,
      m1_menciones: 5,
      m1_porcentaje: 50.0,
      m5_menciones: 3,
      m5_porcentaje: 30.0,
      delta_m1_m0: 30.0,
      tendencia: 'crece',
    },
    {
      habilidad: 'Manejo de Office',
      tipo: 'dura',
      total_menciones: 6,
      m0_menciones: 4,
      m0_porcentaje: 40.0,
      m1_menciones: 2,
      m1_porcentaje: 20.0,
      m5_menciones: 0,
      m5_porcentaje: 0.0,
      delta_m1_m0: -20.0,
      tendencia: 'decrece',
    },
    {
      habilidad: 'Machine Learning e IA',
      tipo: 'dura',
      total_menciones: 4,
      m0_menciones: 0,
      m0_porcentaje: 0.0,
      m1_menciones: 3,
      m1_porcentaje: 30.0,
      m5_menciones: 1,
      m5_porcentaje: 10.0,
      delta_m1_m0: 30.0,
      tendencia: 'emergente_en_m1',
    },
  ],
  totales_respuestas: { '0': 10, '1': 10, '5': 10 },
  totales_con_habilidad: { '0': 8, '1': 9, '5': 7 },
};

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

  it('cambia a la pestaña de comparativa y carga datos longitudinales', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    comp.setTab('comparativa');
    const req = http.expectOne(r => r.url === `${API}/ia/habilidades-comparativa`);
    req.flush(COMPARATIVA_RESPONSE);
    fixture.detectChanges();

    expect(comp.activeTab).toBe('comparativa');
    expect(comp.comparativaData.length).toBe(3);
    expect(comp.comparativaData[0].habilidad).toBe('Gestión de proyectos');
    expect(comp.comparativaData[0].tendencia).toBe('crece');
    expect(comp.totalesConHabilidadMomento['0']).toBe(8);

    const rows = fixture.nativeElement.querySelectorAll('.table-responsive tbody tr');
    expect(rows.length).toBe(3);
  });

  it('asigna correctamente las clases y etiquetas de tendencia y delta', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.getTendenciaBadgeClass('crece')).toBe('badge-crece');
    expect(comp.getTendenciaLabel('crece')).toContain('Crecimiento');

    expect(comp.getTendenciaBadgeClass('decrece')).toBe('badge-decrece');
    expect(comp.getTendenciaLabel('decrece')).toContain('Descenso');

    expect(comp.getTendenciaBadgeClass('emergente_en_m1')).toBe('badge-emergente');
    expect(comp.getTendenciaLabel('emergente_en_m1')).toContain('Emergente en M1');

    expect(comp.getTendenciaBadgeClass('estable')).toBe('badge-estable');
    expect(comp.getTendenciaLabel('estable')).toContain('Estable');

    expect(comp.getDeltaClass(12.5)).toBe('delta-positivo');
    expect(comp.getDeltaClass(-8.0)).toBe('delta-negativo');
    expect(comp.getDeltaClass(0)).toBe('delta-neutro');
  });

  it('permite exportar a Excel y solicita el endpoint correspondiente', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    comp.descargarExcel();
    expect(comp.isExportingExcel).toBe(true);

    const req = http.expectOne(r => r.url === `${API}/ia/habilidades-export`);
    expect(req.request.responseType).toBe('blob');
    req.flush(new Blob(['fake excel content'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));

    expect(comp.isExportingExcel).toBe(false);
  });

  it('permite cambiar a la pestaña de curadas y consultar la lista histórica (IA-15)', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    comp.setTab('curadas');
    expect(comp.activeTab).toBe('curadas');
    expect(comp.isLoadingCuradas).toBe(true);

    const req = http.expectOne(`${API}/ia/habilidades/curadas`);
    req.flush([
      {
        id: 1,
        termino_original: 'docker',
        etiqueta_canonica: 'Docker Containers',
        tipo: 'dura',
        variantes: ['docker', 'contenedores'],
        estado: 'aprobada',
        creado_por_id: 2,
        creado_por_correo: 'coordinador@upb.edu.co',
        fecha_creacion: '2026-10-01T10:00:00Z',
      }
    ]);
    fixture.detectChanges();

    expect(comp.isLoadingCuradas).toBe(false);
    expect(comp.curadasList.length).toBe(1);
    expect(comp.curadasList[0].etiqueta_canonica).toBe('Docker Containers');
  });

  it('abre el modal de aprobación y permite guardar una habilidad curada (IA-15)', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    const cand = { termino: 'flutter', score_tfidf: 0.85, frecuencia_documentos: 4 };
    comp.candidatasEmergentes = [cand];

    comp.abrirModalAprobar(cand);
    expect(comp.curandoItem).toBe(cand);
    expect(comp.modalEtiquetaCanonica).toBe('Flutter');
    expect(comp.modalTipo).toBe('dura');

    comp.modalVariantesStr = 'flutter, dart';
    comp.guardarAprobacion();
    expect(comp.isSavingCuraduria).toBe(true);

    const req = http.expectOne(`${API}/ia/habilidades/curar`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      termino_original: 'flutter',
      etiqueta_canonica: 'Flutter',
      tipo: 'dura',
      variantes: ['flutter', 'dart'],
      estado: 'aprobada',
    });
    req.flush({
      mensaje: 'Habilidad aprobada',
      curada: {
        id: 10,
        termino_original: 'flutter',
        etiqueta_canonica: 'Flutter',
        tipo: 'dura',
        variantes: ['flutter', 'dart'],
        estado: 'aprobada',
        creado_por_id: 1,
        creado_por_correo: 'admin@upb.edu.co',
        fecha_creacion: '2026-10-01T10:00:00Z',
      }
    });

    // Como reload dispara cargarDatosCompletos, flush las peticiones
    http.expectOne(r => r.url === `${API}/ia/habilidades-demandadas`).flush(HABILIDADES_RESPONSE);
    http.expectOne(r => r.url === `${API}/ia/reglas-asociacion`).flush(REGLAS_RESPONSE);

    expect(comp.isSavingCuraduria).toBe(false);
    expect(comp.curandoItem).toBeNull();
    expect(comp.candidatasEmergentes.some(c => c.termino === 'flutter')).toBe(false);
  });
});

