import { CommonModule } from '@angular/common';
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { AnaliticaApi, AnaliticaResumen } from '../../../../data/api/analitica.api';
import { IaApi, PrediccionEmpleabilidadResponse, ComparativaAlgoritmoItem } from '../../../../data/api/ia.api';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { CHART_PALETTE } from '../../../shared/chart-palette';
import { exportChart } from '../../../shared/export-chart';

@Component({
  selector: 'app-analitica',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent, BaseChartDirective],
  templateUrl: './analitica.html',
  styleUrls: ['./analitica.scss'],
})
export class AnaliticaComponent implements OnInit {
  resumen: AnaliticaResumen | null = null;
  prediccion: PrediccionEmpleabilidadResponse | null = null;
  cargandoPrediccion = false;
  isExportingExecutiveReport = false;
  error = '';
  errorPrediccion = '';

  // Controles de horizonte temporal y filtros
  momentoDestino: number = 1;
  filtroPrograma: string = '';
  programasDisponibles: string[] = [];
  comparativaAlgoritmos: ComparativaAlgoritmoItem[] = [];

  // Configuración de gráficos Chart.js
  public barChartType: ChartType = 'bar';
  public isChartReady = false;

  // IA-02: Gráfica de barras apiladas horizontales (probabilidades por programa)
  public stackedProbsChartData: ChartData<'bar', number[], string> = { labels: [], datasets: [] };
  public stackedProbsChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 14,
          font: { size: 12, family: 'Plus Jakarta Sans, sans-serif' },
          padding: 16,
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => ` ${context.dataset.label}: ${context.raw}%`,
        },
      },
    },
    scales: {
      x: {
        stacked: true,
        min: 0,
        max: 100,
        ticks: {
          callback: (value) => `${value}%`,
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      y: {
        stacked: true,
        grid: {
          display: false,
        },
      },
    },
  };

  // IA-03: Gráfica de importancia de factores
  public factoresChartData: ChartData<'bar', number[], string> = { labels: [], datasets: [] };
  public factoresChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => ` Importancia: ${context.raw}%`,
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          callback: (value) => `${value}%`,
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      y: {
        grid: {
          display: false,
        },
      },
    },
  };

  constructor(
    private api: AnaliticaApi,
    private iaApi: IaApi,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.cargarResumen();
    this.cargarPrediccion();
  }

  exportarGrafica(selector: string, nombre: string): void {
    exportChart(selector, nombre);
  }

  cargarResumen() {
    this.api.resumen().subscribe({
      next: (data) => {
        this.resumen = data;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No fue posible cargar la analítica.';
        this.cdr.markForCheck();
      },
    });
  }

  cargarPrediccion() {
    this.cargandoPrediccion = true;
    this.errorPrediccion = '';
    this.cdr.markForCheck();

    this.iaApi
      .prediccionEmpleabilidad({
        momento_origen: 0,
        momento_destino: this.momentoDestino,
        programa: this.filtroPrograma || undefined,
      })
      .subscribe({
        next: (data) => {
          this.prediccion = data;
          this.cargandoPrediccion = false;
          this.comparativaAlgoritmos = data.comparativa_algoritmos || [];

          // Extraer lista de programas únicos si aún no están poblados
          if (data.predicciones_programas && (!this.programasDisponibles || this.programasDisponibles.length === 0)) {
            this.programasDisponibles = data.predicciones_programas.map((p) => p.programa).sort();
          }

          if (data.estado === 'exitoso') {
            this.buildCharts(data);
          } else {
            this.isChartReady = false;
          }
          this.cdr.markForCheck();
        },
        error: () => {
          this.errorPrediccion = 'No fue posible conectar con el servicio predictivo de IA.';
          this.cargandoPrediccion = false;
          this.isChartReady = false;
          this.cdr.markForCheck();
        },
      });
  }

  buildCharts(prediccion: PrediccionEmpleabilidadResponse): void {
    if (!prediccion || prediccion.estado !== 'exitoso') {
      this.isChartReady = false;
      return;
    }

    // IA-02: Gráfica de distribución de probabilidades por programa (barras apiladas)
    const progs = prediccion.predicciones_programas || [];
    this.stackedProbsChartData = {
      labels: progs.map((p) => p.programa),
      datasets: [
        {
          label: 'Empleado',
          data: progs.map((p) => p.probabilidad_empleado),
          backgroundColor: CHART_PALETTE[2], // verde éxito #137a47
          borderRadius: 2,
        },
        {
          label: 'Independiente',
          data: progs.map((p) => p.probabilidad_independiente),
          backgroundColor: CHART_PALETTE[1], // índigo analítico #6366f1
          borderRadius: 2,
        },
        {
          label: 'Estudiante',
          data: progs.map((p) => p.probabilidad_estudiante),
          backgroundColor: CHART_PALETTE[3], // amarillo secundario #ffc20e
          borderRadius: 2,
        },
        {
          label: 'Sin empleo',
          data: progs.map((p) => p.probabilidad_sin_empleo),
          backgroundColor: CHART_PALETTE[0], // rojo primario #e31e24
          borderRadius: 2,
        },
      ],
    };

    // IA-03: Gráfica de importancia de factores
    const factores = prediccion.importancia_factores || [];
    this.factoresChartData = {
      labels: factores.map((f) => f.factor),
      datasets: [
        {
          data: factores.map((f) => f.importancia),
          backgroundColor: CHART_PALETTE[1], // índigo analítico #6366f1
          borderRadius: 4,
        },
      ],
    };

    this.isChartReady = true;
  }

  // IA-04: Helpers para Heatmap de Matriz de Confusión
  getMaxMatrizConfusion(): number {
    if (!this.prediccion?.matriz_confusion?.matriz?.length) return 1;
    let max = 0;
    for (const fila of this.prediccion.matriz_confusion.matriz) {
      for (const val of fila) {
        if (val > max) max = val;
      }
    }
    return max > 0 ? max : 1;
  }

  getHeatmapBg(rowIdx: number, colIdx: number, valor: number): string {
    if (valor === 0) return 'rgba(0, 0, 0, 0.02)';
    const max = this.getMaxMatrizConfusion();
    const ratio = Math.min(valor / max, 1);
    if (rowIdx === colIdx) {
      // Diagonal: aciertos (verde institucional)
      const alpha = 0.15 + 0.65 * ratio;
      return `rgba(19, 122, 71, ${alpha.toFixed(2)})`;
    }
    // Fuera de diagonal: confusiones (rojo advertencia)
    const alpha = 0.10 + 0.55 * ratio;
    return `rgba(227, 30, 36, ${alpha.toFixed(2)})`;
  }

  getHeatmapTextColor(rowIdx: number, colIdx: number, valor: number): string {
    if (valor === 0) return 'var(--muted)';
    const max = this.getMaxMatrizConfusion();
    const ratio = valor / max;
    if (ratio > 0.65) return '#ffffff';
    return 'var(--heading)';
  }

  getFilaTotal(fila: number[]): number {
    return (fila || []).reduce((acc, curr) => acc + curr, 0);
  }

  getFilaPorcentaje(valor: number, fila: number[]): number {
    const total = this.getFilaTotal(fila);
    if (total === 0) return 0;
    return Math.round((valor / total) * 100);
  }

  formatClaseLabel(clase: string): string {
    const mapa: Record<string, string> = {
      empleado: 'Empleado',
      independiente: 'Independiente',
      estudiante: 'Estudiante',
      sin_empleo: 'Sin empleo',
    };
    return mapa[clase?.toLowerCase()] || (clase ? clase.charAt(0).toUpperCase() + clase.slice(1) : '');
  }

  cambiarHorizonte(momento: number) {
    if (this.momentoDestino === momento) return;
    this.momentoDestino = momento;
    this.cargarPrediccion();
  }

  onFiltrarPrograma(programa: string) {
    if (this.filtroPrograma === programa) return;
    this.filtroPrograma = programa;
    this.cargarPrediccion();
  }

  getBadgeClass(nivel: string): string {
    switch (nivel?.toLowerCase()) {
      case 'alto':
        return 'badge-danger';
      case 'medio':
        return 'badge-warning';
      case 'bajo':
        return 'badge-success';
      default:
        return 'badge-neutral';
    }
  }

  getRobustnessBadgeClass(color: string): string {
    switch (color?.toLowerCase()) {
      case 'verde':
        return 'badge-success';
      case 'amarillo':
        return 'badge-warning';
      case 'rojo':
        return 'badge-danger';
      default:
        return 'badge-neutral';
    }
  }

  descargarReporteEjecutivo(): void {
    this.isExportingExecutiveReport = true;
    this.iaApi
      .exportarPrediccionExcel({
        momento_origen: 0,
        momento_destino: this.momentoDestino,
        programa: this.filtroPrograma || undefined,
      })
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `informe_predictivo_M0_a_M${this.momentoDestino}_oeupb.xlsx`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
          this.isExportingExecutiveReport = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Error al exportar reporte ejecutivo:', err);
          this.isExportingExecutiveReport = false;
          this.cdr.markForCheck();
        },
      });
  }
}
