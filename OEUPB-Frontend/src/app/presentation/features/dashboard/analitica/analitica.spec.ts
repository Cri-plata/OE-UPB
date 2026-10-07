import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { AnaliticaComponent } from './analitica';
import { API_BASE_URL } from '../../../../data/api/api.config';

const RESUMEN_MOCK = {
  textos_analizados: 25,
  competencias: [
    { categoria: 'Trabajo en equipo', frecuencia: 10 },
    { categoria: 'Liderazgo', frecuencia: 8 },
  ],
  alertas: [
    {
      tipo: 'empleabilidad',
      programa: 'Ingeniería de Sistemas',
      momento: 1,
      severidad: 'alta',
      mensaje: 'Baja tasa de inserción laboral observada.',
      valor: 45.0,
      muestra: 20,
    },
  ],
};

const PREDICCION_MOCK = {
  estado: 'exitoso',
  mensaje: 'Modelo de análisis entrenado con GradientBoostingClassifier.',
  total_trayectorias: 91,
  precision_modelo: 59.3,
  f1_score: 0.343,
  estrategia_balanceo: 'Ponderación adaptativa de clases activa (Cost-Sensitive Learning)',
  programas_analizados: 2,
  egresados_en_riesgo: 0,
  importancia_factores: [
    { factor: 'Nivel salarial inicial', importancia: 34.1 },
    { factor: 'Estado laboral inicial (M0)', importancia: 20.3 },
  ],
  predicciones_programas: [
    {
      programa: 'Ingeniería de Sistemas',
      total_egresados: 25,
      probabilidad_empleado: 75.0,
      probabilidad_independiente: 15.0,
      probabilidad_estudiante: 5.0,
      probabilidad_sin_empleo: 5.0,
      nivel_riesgo: 'Bajo',
      rango_salarial_estimado: '2–4 SMLV',
    },
    {
      programa: 'Derecho',
      total_egresados: 20,
      probabilidad_empleado: 60.0,
      probabilidad_independiente: 25.0,
      probabilidad_estudiante: 5.0,
      probabilidad_sin_empleo: 10.0,
      nivel_riesgo: 'Bajo',
      rango_salarial_estimado: '2–4 SMLV',
    },
  ],
  alertas_riesgo: [],
  matriz_confusion: {
    clases: ['empleado', 'independiente', 'sin_empleo'],
    matriz: [
      [55, 5, 2],
      [4, 12, 1],
      [3, 1, 8],
    ],
  },
  indicadores_robustez: {
    nivel_general: 'Media',
    color_general: 'amarillo',
    muestra: {
      status: 'moderado',
      color: 'amarillo',
      trayectorias: 91,
      observacion: 'Muestra longitudinal moderada (91 trayectorias).',
    },
    balance_clases: {
      status: 'balanceado',
      color: 'verde',
      min_porcentaje: 13.2,
      observacion: 'Distribución equilibrada.',
    },
    precision: {
      status: 'moderada',
      color: 'amarillo',
      accuracy: 59.3,
      observacion: 'Concordancia moderada.',
    },
    observaciones: ['Muestra longitudinal moderada.'],
  },
  comparativa_algoritmos: [
    { algoritmo: 'Gradient Boosting', accuracy: 59.3, f1_score: 0.343, tiempo_ms: 12.4, seleccionado: true },
    { algoritmo: 'Random Forest', accuracy: 57.1, f1_score: 0.320, tiempo_ms: 8.1, seleccionado: false },
    { algoritmo: 'Regresión Logística', accuracy: 54.0, f1_score: 0.301, tiempo_ms: 4.2, seleccionado: false },
  ],
  validacion_temporal: {
    disponible: true,
    cohorte_evaluada: 2024,
    tamano_muestra_prueba: 25,
    tamano_muestra_entrenamiento: 66,
    accuracy_temporal: 64.0,
    f1_temporal: 0.380,
    diagnostico_estabilidad: 'Alta (Generalización temporal consistente)',
    color_estabilidad: 'verde',
  },
};

describe('AnaliticaComponent', () => {
  let http: HttpTestingController;

  function crear() {
    TestBed.configureTestingModule({
      imports: [AnaliticaComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    const fixture = TestBed.createComponent(AnaliticaComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();

    http.expectOne(`${API_BASE_URL}/analitica/resumen`).flush(RESUMEN_MOCK);
    http.expectOne((r) => r.url === `${API_BASE_URL}/ia/prediccion-empleabilidad`).flush(PREDICCION_MOCK);
    fixture.detectChanges();

    return fixture;
  }

  afterEach(() => {
    http.verify();
  });

  it('debe inicializarse y cargar tanto el resumen como la predicción', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.resumen).toBeTruthy();
    expect(comp.resumen?.competencias.length).toBe(2);
    expect(comp.prediccion).toBeTruthy();
    expect(comp.prediccion?.estado).toBe('exitoso');
    expect(comp.prediccion?.precision_modelo).toBe(59.3);
    expect(comp.prediccion?.f1_score).toBe(0.343);
    expect(comp.prediccion?.predicciones_programas.length).toBe(2);
    expect(comp.programasDisponibles).toEqual(['Derecho', 'Ingeniería de Sistemas']);
    expect(comp.cargandoPrediccion).toBe(false);
  });

  it('debe clasificar badges de nivel de riesgo correctamente', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.getBadgeClass('Alto')).toBe('badge-danger');
    expect(comp.getBadgeClass('alto')).toBe('badge-danger');
    expect(comp.getBadgeClass('Medio')).toBe('badge-warning');
    expect(comp.getBadgeClass('medio')).toBe('badge-warning');
    expect(comp.getBadgeClass('Bajo')).toBe('badge-success');
    expect(comp.getBadgeClass('bajo')).toBe('badge-success');
    expect(comp.getBadgeClass('otro')).toBe('badge-neutral');
  });

  it('debe cambiar de horizonte temporal a Momento 5 y refrescar la consulta', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    comp.cambiarHorizonte(5);
    expect(comp.cargandoPrediccion).toBe(true);

    const reqM5 = http.expectOne((r) => r.url === `${API_BASE_URL}/ia/prediccion-empleabilidad`);
    expect(reqM5.request.params.get('momento_destino')).toBe('5');

    reqM5.flush({
      estado: 'insuficiente_datos',
      mensaje: 'Se requieren al menos 30 trayectorias longitudinales hacia Momento 5.',
      total_trayectorias: 0,
      precision_modelo: 0,
      f1_score: 0,
      programas_analizados: 0,
      egresados_en_riesgo: 0,
      importancia_factores: [],
      predicciones_programas: [],
      alertas_riesgo: [],
      matriz_confusion: { clases: [], matriz: [] },
    });

    fixture.detectChanges();

    expect(comp.prediccion?.estado).toBe('insuficiente_datos');
    expect(comp.momentoDestino).toBe(5);
    expect(comp.cargandoPrediccion).toBe(false);
  });

  it('debe aplicar filtro por programa y enviar parámetro al backend', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    comp.onFiltrarPrograma('Ingeniería de Sistemas');
    expect(comp.filtroPrograma).toBe('Ingeniería de Sistemas');

    const reqFiltro = http.expectOne((r) => r.url === `${API_BASE_URL}/ia/prediccion-empleabilidad`);
    expect(reqFiltro.request.params.get('programa')).toBe('Ingeniería de Sistemas');

    reqFiltro.flush(PREDICCION_MOCK);
    fixture.detectChanges();

    expect(comp.prediccion?.estado).toBe('exitoso');
    expect(comp.cargandoPrediccion).toBe(false);
  });

  it('construye las gráficas Chart.js al cargar predicción exitosa', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.isChartReady).toBe(true);
    // IA-02: Barras apiladas de distribución de probabilidades
    expect(comp.stackedProbsChartData.labels?.length).toBe(2);
    expect(comp.stackedProbsChartData.datasets.length).toBe(4);
    expect(comp.stackedProbsChartData.datasets[0].label).toBe('Empleado');
    expect(comp.stackedProbsChartData.datasets[0].data).toEqual([75.0, 60.0]);
    expect(comp.stackedProbsChartData.datasets[1].label).toBe('Independiente');
    expect(comp.stackedProbsChartData.datasets[2].label).toBe('Estudiante');
    expect(comp.stackedProbsChartData.datasets[3].label).toBe('Sin empleo');

    // IA-03: Barras horizontales de factores influyentes
    expect(comp.factoresChartData.labels?.length).toBe(2);
    expect(comp.factoresChartData.datasets[0].data).toEqual([34.1, 20.3]);
  });

  it('formatea etiquetas y calcula helpers de la matriz de confusión (IA-04)', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.formatClaseLabel('empleado')).toBe('Empleado');
    expect(comp.formatClaseLabel('independiente')).toBe('Independiente');
    expect(comp.formatClaseLabel('sin_empleo')).toBe('Sin empleo');
    expect(comp.formatClaseLabel('estudiante')).toBe('Estudiante');

    expect(comp.getMaxMatrizConfusion()).toBe(55);
    expect(comp.getFilaTotal([55, 5, 2])).toBe(62);
    expect(comp.getFilaPorcentaje(55, [55, 5, 2])).toBe(89);

    // Diagonal: tinte verde
    const bgDiag = comp.getHeatmapBg(0, 0, 55);
    expect(bgDiag).toContain('19, 122, 71');

    // Fuera de diagonal: tinte rojo
    const bgOff = comp.getHeatmapBg(0, 1, 5);
    expect(bgOff).toContain('227, 30, 36');

    // Cero: neutral transparente
    const bgCero = comp.getHeatmapBg(0, 0, 0);
    expect(bgCero).toContain('rgba(0, 0, 0, 0.02)');
  });

  it('permite llamar a exportarGrafica sin errores', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(() => comp.exportarGrafica('#grafica-factores canvas', 'factores.png')).not.toThrow();
    expect(() => comp.exportarGrafica('#grafica-distribucion-probabilidades canvas', 'dist.png')).not.toThrow();
  });

  it('procesa el semáforo de robustez estadística (IA-13) correctamente', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.prediccion?.indicadores_robustez).toBeTruthy();
    expect(comp.prediccion?.indicadores_robustez?.nivel_general).toBe('Media');
    expect(comp.prediccion?.indicadores_robustez?.color_general).toBe('amarillo');
    expect(comp.prediccion?.indicadores_robustez?.muestra.status).toBe('moderado');

    expect(comp.getRobustnessBadgeClass('verde')).toBe('badge-success');
    expect(comp.getRobustnessBadgeClass('amarillo')).toBe('badge-warning');
    expect(comp.getRobustnessBadgeClass('rojo')).toBe('badge-danger');
    expect(comp.getRobustnessBadgeClass('otro')).toBe('badge-neutral');
  });

  it('renderiza la comparativa multi-algoritmo (IA-10)', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    expect(comp.comparativaAlgoritmos.length).toBe(3);
    expect(comp.comparativaAlgoritmos[0].algoritmo).toBe('Gradient Boosting');
    expect(comp.comparativaAlgoritmos[0].seleccionado).toBe(true);

    const rows = fixture.nativeElement.querySelectorAll('.table-card table.data-table tbody tr');
    // Al menos las filas de la tabla de algoritmos deben estar presentes
    expect(rows.length).toBeGreaterThanOrEqual(3);
  });

  it('permite descargar el reporte ejecutivo en Excel (IA-14)', () => {
    const fixture = crear();
    const comp = fixture.componentInstance;

    comp.descargarReporteEjecutivo();
    expect(comp.isExportingExecutiveReport).toBe(true);

    const req = http.expectOne(r => r.url === `${API_BASE_URL}/ia/prediccion-export`);
    expect(req.request.responseType).toBe('blob');
    req.flush(new Blob(['fake excel content'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));

    expect(comp.isExportingExecutiveReport).toBe(false);
  });

  it('incluye tooltips contextuales en las métricas clave (IA-11)', () => {
    const fixture = crear();
    const tooltips = fixture.nativeElement.querySelectorAll('.tooltip-trigger');
    expect(tooltips.length).toBeGreaterThanOrEqual(4);
    const firstTitle = tooltips[0].getAttribute('title');
    expect(firstTitle).toContain('Stratified K-Fold');
  });

  it('debe renderizar la sección de validación temporal / backtesting longitudinal (IA-17)', () => {
    const fixture = crear();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.backtesting-card')).toBeTruthy();
    expect(compiled.textContent).toContain('Validación Temporal por Cohorte / Backtesting (IA-17)');
    expect(compiled.textContent).toContain('Año 2024');
    expect(compiled.textContent).toContain('64%');
  });

  it('muestra el badge y texto de ponderación balanceada en la matriz de confusión', () => {
    const fixture = crear();
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Ponderación Balanceada Activa');
    expect(compiled.textContent).toContain('Cost-Sensitive Learning');
  });

  it('presenta el modelo como modelo de análisis y no como predictivo (ADR-021)', () => {
    const fixture = crear();
    const texto = ((fixture.nativeElement as HTMLElement).textContent || '').toLowerCase();
    // Los atributos title (tooltips) también son texto visible para el usuario.
    const tooltips = Array.from((fixture.nativeElement as HTMLElement).querySelectorAll('[title]'))
      .map(e => (e.getAttribute('title') || '').toLowerCase()).join(' ');

    expect(texto).toContain('modelo de análisis de empleabilidad');
    for (const prohibido of ['predictiv', 'predicci', 'predicho']) {
      expect(texto).not.toContain(prohibido);
      expect(tooltips).not.toContain(prohibido);
    }
  });
});
