import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
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
  selector: 'app-tendencias',
  standalone: true,
  imports: [CommonModule, SidebarComponent, BaseChartDirective],
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
  }

  loadData() {
    this.isChartReady = false;
    this.cdr.detectChanges();

    this.reportesApi.tendencias(this.currentIndicator).subscribe({
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
        console.error("Error cargando tendencias", err);
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

  get graficaKey(): string { return `tendencias_${this.currentIndicator}`; }

  publicar() {
    if (!confirm('Confirmo que revisé la privacidad de esta gráfica. Se publicarán métricas agregadas recalculadas por el sistema; las categorías con menos de 5 observaciones se agrupan u omiten.')) return;
    const payload: PublicacionCreate = {
      grafica_key: this.graficaKey,
      titulo: `Evolución histórica: ${this.currentIndicatorName}`,
      definicion: { origen: 'tendencias', tipo_visualizacion: this.chartType as 'line' | 'bar', indicador: this.currentIndicator },
      aprobada_privacidad: true
    };
    this.publicacion.publicar(payload.grafica_key, payload);
  }

  retirar() {
    if (!confirm('¿Retirar esta publicación? Dejará de ser visible inmediatamente.')) return;
    this.publicacion.retirar(this.graficaKey);
  }
}
