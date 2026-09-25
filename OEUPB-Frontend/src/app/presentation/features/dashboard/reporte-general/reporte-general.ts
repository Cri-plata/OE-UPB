import { Component, OnInit, ChangeDetectorRef, inject, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { ReportesApi } from '../../../../data/api/reportes.api';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import { PublicacionControl } from '../../../shared/publicacion-control';
import { PublicacionCreate } from '../../../../data/api/generated-api.models';
import { CHART_PALETTE } from '../../../shared/chart-palette';
import { exportChart } from '../../../shared/export-chart';

@Component({
  selector: 'app-reporte-general',
  standalone: true,
  imports: [CommonModule, SidebarComponent, BaseChartDirective],
  providers: [PublicacionControl],
  templateUrl: './reporte-general.html',
  styleUrls: ['./reporte-general.scss']
})
export class ReporteGeneralComponent implements OnInit {
  exportarGrafica(selector: string, nombre: string) { exportChart(selector, nombre); }
  kpis: any = null;
  isChartReady = false;
  readonly publicacion = inject(PublicacionControl);

  public pieChartType: ChartType = 'doughnut';
  public barChartType: ChartType = 'bar';

  public pieChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public pieChartData: ChartData<ChartType, number[], string | string[]> = { labels: [], datasets: [] };

  public barChartOptions: ChartConfiguration['options'] = { responsive: true, maintainAspectRatio: false };
  public barChartData: ChartData<ChartType, number[], string | string[]> = { labels: [], datasets: [] };

  @ViewChild('colorPickerPie') colorPickerPie!: ElementRef<HTMLInputElement>;
  @ViewChild('colorPickerBar') colorPickerBar!: ElementRef<HTMLInputElement>;
  clickedBarIndex: number | null = null;
  clickedPieIndex: number | null = null;

  constructor(private reportesApi: ReportesApi, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.publicacion.cargarPropias();
    this.reportesApi.general().subscribe({
      next: (data) => {
        this.kpis = {
          total_egresados: data.total_egresados,
          tasa_empleabilidad: data.tasa_empleabilidad,
          promedio_salarial: data.promedio_salarial
        };

        const programas = Object.keys(data.distribucion_programas);
        const cantidades = Object.values(data.distribucion_programas) as number[];
        
        // Agregar la cantidad exacta al label
        const labelsConCantidad = programas.map((prog, i) => `${prog} (${cantidades[i]})`);
        
        const baseColors = CHART_PALETTE;
        // Asegurar que cada barra tenga su propio color independiente en memoria para que no se vinculen al editarlos
        const bgColors = programas.map((_, i) => baseColors[i % baseColors.length]);

        this.pieChartData = {
          labels: labelsConCantidad,
          datasets: [{ data: cantidades, backgroundColor: bgColors }]
        };

        const satis_keys = Object.keys(data.nivel_satisfaccion);
        const satis_vals = Object.values(data.nivel_satisfaccion) as number[];

        this.barChartData = {
          labels: satis_keys,
          datasets: [
            { data: satis_vals, label: 'Satisfacción Promedio', backgroundColor: CHART_PALETTE.slice(0, 4) }
          ]
        };

        this.isChartReady = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error("Error cargando reporte general", err);
      }
    });
  }

  publicar(key: string, titulo: string, indicador: 'distribucion_programas' | 'satisfaccion', tipo: ChartType) {
    if (!confirm('Confirmo que revisé la privacidad de esta gráfica. Se publicarán métricas agregadas recalculadas por el sistema; las categorías con menos de 5 observaciones se agrupan u omiten.')) return;
    const payload: PublicacionCreate = {
      grafica_key: key,
      titulo,
      definicion: { origen: 'reporte_general', tipo_visualizacion: tipo as PublicacionCreate['definicion']['tipo_visualizacion'], indicador },
      aprobada_privacidad: true
    };
    this.publicacion.publicar(key, payload);
  }

  retirar(key: string) {
    if (!confirm('¿Retirar esta publicación? Dejará de ser visible inmediatamente.')) return;
    this.publicacion.retirar(key);
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

