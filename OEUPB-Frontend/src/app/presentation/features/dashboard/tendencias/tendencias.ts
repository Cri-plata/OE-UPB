import { Component, OnInit, ChangeDetectorRef, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { FiltrosAnaliticos, ReportesApi, SIN_FILTROS } from '../../../../data/api/reportes.api';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { PublicacionControl } from '../../../shared/publicacion-control';
import { ComparacionResponse, PublicacionCreate } from '../../../../data/api/generated-api.models';
import { FiltrosAnaliticosComponent } from '../../../shared/components/filtros-analiticos/filtros-analiticos';
import { claveConFiltros, definicionDeFiltros, descripcionFiltros } from '../../../shared/filtros-grafica';
import { mensajeDeError } from '../../../shared/mensaje-error';
import { CHART_PALETTE } from '../../../shared/chart-palette';
import { exportChart } from '../../../shared/export-chart';

@Component({
  selector: 'app-tendencias',
  standalone: true,
  imports: [CommonModule, SidebarComponent, BaseChartDirective, FiltrosAnaliticosComponent],
  providers: [PublicacionControl],
  templateUrl: './tendencias.html',
  styleUrls: ['./tendencias.scss']
})
export class TendenciasComponent implements OnInit {
  exportarGrafica() { exportChart('#grafica-tendencias canvas', 'tendencias.png'); }
  isChartReady = false;
  chartType: ChartType = 'line';
  currentIndicator = 'empleabilidad';
  currentIndicatorName = 'Tasa de Empleabilidad';
  readonly publicacion = inject(PublicacionControl);
  filtros: FiltrosAnaliticos = SIN_FILTROS;
  errorCarga = '';

  // Comparación longitudinal entre dos momentos (HU-08); estado en signals.
  readonly momentoInicial = signal(0);
  readonly momentoFinal = signal(1);
  readonly indicadorComparacion = signal<'empleabilidad' | 'salario'>('empleabilidad');
  readonly comparacion = signal<ComparacionResponse | null>(null);
  readonly cargandoComparacion = signal(false);
  readonly errorComparacion = signal('');
  readonly programasComparables = computed(() => (this.comparacion()?.programas ?? []).filter(p => p.suficiente));
  readonly programasInsuficientes = computed(() => (this.comparacion()?.programas ?? []).filter(p => !p.suficiente));
  readonly comparacionChartData = computed<ChartData<'bar', (number | null)[], string>>(() => ({
    labels: this.programasComparables().map(p => `${p.programa} (${p.pares} pares)`),
    datasets: [
      { label: `Momento ${this.momentoInicial()}`, data: this.programasComparables().map(p => p.valor_inicial ?? null), backgroundColor: CHART_PALETTE[1] },
      { label: `Momento ${this.momentoFinal()}`, data: this.programasComparables().map(p => p.valor_final ?? null), backgroundColor: CHART_PALETTE[0] },
    ],
  }));
  readonly comparacionChartOptions: ChartConfiguration<'bar'>['options'] = { responsive: true, maintainAspectRatio: false };

  public lineChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: { family: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif", size: 12 }
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        titleColor: '#000',
        bodyColor: '#333',
        borderColor: '#ddd',
        borderWidth: 1,
        padding: 12,
        boxPadding: 6
      }
    },
    scales: {
      x: {
        grid: { display: false }
      },
      y: {
        beginAtZero: false,
        grid: { color: 'rgba(0, 0, 0, 0.05)' }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  };
  
  public lineChartData: ChartData<ChartType, (number|null)[], string> = { labels: [], datasets: [] };

  constructor(private reportesApi: ReportesApi, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.publicacion.cargarPropias();
    this.loadData();
    this.cargarComparacion();
  }

  aplicarFiltros(filtros: FiltrosAnaliticos) {
    this.filtros = filtros;
    this.loadData();
    this.cargarComparacion();
  }

  cargarComparacion() {
    if (this.momentoInicial() === this.momentoFinal()) {
      this.comparacion.set(null);
      this.errorComparacion.set('Seleccione dos momentos distintos.');
      return;
    }
    this.cargandoComparacion.set(true);
    this.errorComparacion.set('');
    this.reportesApi.comparacion(this.momentoInicial(), this.momentoFinal(), this.indicadorComparacion(), this.filtros).subscribe({
      next: comparacion => {
        this.comparacion.set(comparacion);
        this.cargandoComparacion.set(false);
      },
      error: (err: unknown) => {
        this.comparacion.set(null);
        this.errorComparacion.set(mensajeDeError(err, 'No fue posible calcular la comparación.'));
        this.cargandoComparacion.set(false);
      }
    });
  }

  cambiarComparacion(campo: 'inicial' | 'final' | 'indicador', valor: string) {
    if (campo === 'inicial') this.momentoInicial.set(Number(valor));
    if (campo === 'final') this.momentoFinal.set(Number(valor));
    if (campo === 'indicador') this.indicadorComparacion.set(valor as 'empleabilidad' | 'salario');
    this.cargarComparacion();
  }

  loadData() {
    this.isChartReady = false;
    this.errorCarga = '';
    this.cdr.detectChanges();

    this.reportesApi.tendencias(this.currentIndicator, this.filtros).subscribe({
      next: (data) => {
        const colors = CHART_PALETTE;
        
        // Asignar colores a los datasets
        this.lineChartData = {
          labels: data.labels,
          datasets: data.datasets.map((dataset, i) => ({
            label: dataset.label,
            data: dataset.data,
            borderColor: colors[i % colors.length],
            backgroundColor: colors[i % colors.length] + '33',
            borderWidth: dataset.borderWidth ?? undefined,
            pointRadius: dataset.pointRadius ?? undefined,
            tension: dataset.tension ?? undefined,
            spanGaps: dataset.spanGaps ?? undefined,
            fill: false,
          }))
        };

        this.isChartReady = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.errorCarga = mensajeDeError(err, 'No fue posible cargar las tendencias.');
        this.cdr.detectChanges();
      }
    });
  }

  changeIndicator(event: any) {
    this.currentIndicator = event.target.value;
    const select = event.target;
    this.currentIndicatorName = select.options[select.selectedIndex].text;
    
    this.loadData();
  }

  changeChartType(event: any) {
    this.chartType = event.target.value as ChartType;
    this.cdr.detectChanges();
  }

  get graficaKey(): string { return claveConFiltros(`tendencias_${this.currentIndicator}`, { ...this.filtros, momento: undefined }); }

  publicar() {
    if (!confirm('Confirmo que revisé la privacidad de esta gráfica. Se publicarán métricas agregadas recalculadas por el sistema; las categorías con menos de 5 observaciones se agrupan u omiten.')) return;
    const payload: PublicacionCreate = {
      grafica_key: this.graficaKey,
      titulo: `Evolución histórica: ${this.currentIndicatorName}${descripcionFiltros({ ...this.filtros, momento: undefined })}`,
      definicion: {
        origen: 'tendencias',
        tipo_visualizacion: this.chartType as 'line' | 'bar',
        indicador: this.currentIndicator,
        ...definicionDeFiltros({ ...this.filtros, momento: undefined }),
      },
      aprobada_privacidad: true
    };
    this.publicacion.publicar(payload.grafica_key, payload);
  }

  retirar() {
    if (!confirm('¿Retirar esta publicación? Dejará de ser visible inmediatamente.')) return;
    this.publicacion.retirar(this.graficaKey);
  }
}
