import { Component, OnInit, ChangeDetectorRef, inject, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { FiltrosAnaliticos, ReportesApi, SIN_FILTROS } from '../../../../data/api/reportes.api';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { PublicacionControl } from '../../../shared/publicacion-control';
import { KpisResponse, PublicacionCreate } from '../../../../data/api/generated-api.models';
import { FiltrosAnaliticosComponent } from '../../../shared/components/filtros-analiticos/filtros-analiticos';
import { claveConFiltros, definicionDeFiltros, descripcionFiltros } from '../../../shared/filtros-grafica';
import { CHART_PALETTE } from '../../../shared/chart-palette';
import { exportChart } from '../../../shared/export-chart';
import { mensajeDeError } from '../../../shared/mensaje-error';

@Component({
  selector: 'app-reporte-general',
  standalone: true,
  imports: [CommonModule, SidebarComponent, BaseChartDirective, FiltrosAnaliticosComponent],
  providers: [PublicacionControl],
  templateUrl: './reporte-general.html',
  styleUrls: ['./reporte-general.scss']
})
export class ReporteGeneralComponent implements OnInit {
  exportarGrafica(selector: string, nombre: string) { exportChart(selector, nombre); }
  kpis: KpisResponse | null = null;
  isChartReady = false;
  errorCarga = '';
  filtros: FiltrosAnaliticos = SIN_FILTROS;
  readonly publicacion = inject(PublicacionControl);

  public pieChartType: ChartType = 'doughnut';
  public barChartType: ChartType = 'bar';

  public pieChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public pieChartData: ChartData<ChartType, number[], string | string[]> = { labels: [], datasets: [] };

  public barChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public barChartData: ChartData<ChartType, number[], string | string[]> = { labels: [], datasets: [] };

  public estadoChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } };
  public estadoChartData: ChartData<'bar', number[], string> = { labels: [], datasets: [] };

  @ViewChild('colorPickerPie') colorPickerPie!: ElementRef<HTMLInputElement>;
  @ViewChild('colorPickerBar') colorPickerBar!: ElementRef<HTMLInputElement>;
  clickedBarIndex: number | null = null;
  clickedPieIndex: number | null = null;

  constructor(private reportesApi: ReportesApi, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.publicacion.cargarPropias();
    this.cargar();
  }

  aplicarFiltros(filtros: FiltrosAnaliticos) {
    this.filtros = filtros;
    this.cargar();
  }

  cargar() {
    this.isChartReady = false;
    this.errorCarga = '';
    this.reportesApi.general(this.filtros).subscribe({
      next: (data) => {
        this.kpis = data;

        const programas = Object.keys(data.distribucion_programas);
        const cantidades = Object.values(data.distribucion_programas) as number[];
        // Agregar la cantidad exacta al label
        const labelsConCantidad = programas.map((prog, i) => `${prog} (${cantidades[i]})`);
        // Asegurar que cada barra tenga su propio color independiente en memoria para que no se vinculen al editarlos
        const bgColors = programas.map((_, i) => CHART_PALETTE[i % CHART_PALETTE.length]);
        this.pieChartData = {
          labels: labelsConCantidad,
          datasets: [{ data: cantidades, backgroundColor: bgColors }]
        };

        this.barChartData = {
          labels: Object.keys(data.nivel_satisfaccion),
          datasets: [
            { data: Object.values(data.nivel_satisfaccion) as number[], label: 'Satisfacción Promedio', backgroundColor: CHART_PALETTE.slice(0, 4) }
          ]
        };

        const estados = data.distribucion_estado_laboral;
        this.estadoChartData = {
          labels: ['Empleado', 'Independiente', 'Estudiante', 'Sin empleo'],
          datasets: [{
            data: [estados['empleado'] ?? 0, estados['independiente'] ?? 0, estados['estudiante'] ?? 0, estados['sin_empleo'] ?? 0],
            label: 'Egresados',
            backgroundColor: CHART_PALETTE.slice(0, 4),
          }]
        };

        this.isChartReady = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.errorCarga = mensajeDeError(err, 'No fue posible cargar el reporte general.');
        this.cdr.detectChanges();
      }
    });
  }

  /** Clave de publicación del filtro vigente: cada combinación de filtros es una gráfica propia. */
  clave(base: string): string {
    return claveConFiltros(base, this.filtros);
  }

  publicar(base: string, titulo: string, indicador: 'distribucion_programas' | 'satisfaccion' | 'estado_laboral', tipo: ChartType) {
    if (!confirm('Confirmo que revisé la privacidad de esta gráfica. Se publicarán métricas agregadas recalculadas por el sistema; las categorías con menos de 5 observaciones se agrupan u omiten.')) return;
    const key = this.clave(base);
    const payload: PublicacionCreate = {
      grafica_key: key,
      titulo: `${titulo}${descripcionFiltros(this.filtros)}`,
      definicion: {
        origen: 'reporte_general',
        tipo_visualizacion: tipo as PublicacionCreate['definicion']['tipo_visualizacion'],
        indicador,
        ...definicionDeFiltros(this.filtros),
      },
      aprobada_privacidad: true
    };
    this.publicacion.publicar(key, payload);
  }

  retirar(base: string) {
    if (!confirm('¿Retirar esta publicación? Dejará de ser visible inmediatamente.')) return;
    this.publicacion.retirar(this.clave(base));
  }

  changePieChartType(event: any) {
    this.pieChartType = event.target.value as ChartType;
    this.cdr.detectChanges();
  }

  changeBarChartType(event: any) {
    this.barChartType = event.target.value as ChartType;
    this.cdr.detectChanges();
  }

  onChartClickPie({ event, active }: { event?: any, active?: any[] }) {
    if (active && active.length > 0) {
      this.clickedPieIndex = active[0].index;
      if (this.colorPickerPie) {
        this.colorPickerPie.nativeElement.click();
      }
    }
  }

  onColorChangePie(event: any) {
    const newColor = event.target.value;
    if (this.clickedPieIndex !== null && this.pieChartData.datasets && this.pieChartData.datasets.length > 0) {
      const bgColors = this.pieChartData.datasets[0].backgroundColor as string[];
      bgColors[this.clickedPieIndex] = newColor;
      
      this.pieChartData = {
        labels: this.pieChartData.labels,
        datasets: [{
          ...this.pieChartData.datasets[0],
          backgroundColor: [...bgColors]
        }]
      };
      this.cdr.detectChanges();
    }
    this.clickedPieIndex = null;
  }
  onChartClickBar({ event, active }: { event?: any, active?: any[] }) {
    if (active && active.length > 0) {
      this.clickedBarIndex = active[0].index;
      if (this.colorPickerBar) {
        this.colorPickerBar.nativeElement.click();
      }
    }
  }

  onColorChangeBar(event: any) {
    const newColor = event.target.value;
    if (this.clickedBarIndex !== null && this.barChartData.datasets && this.barChartData.datasets.length > 0) {
      const bgColors = this.barChartData.datasets[0].backgroundColor as string[];
      bgColors[this.clickedBarIndex] = newColor;
      
      this.barChartData = {
        labels: this.barChartData.labels,
        datasets: [{
          ...this.barChartData.datasets[0],
          backgroundColor: [...bgColors]
        }]
      };
      this.cdr.detectChanges();
    }
    this.clickedBarIndex = null;
  }
}

