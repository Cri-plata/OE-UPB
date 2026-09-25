import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { ReportesApi } from '../../../../data/api/reportes.api';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartType } from 'chart.js';
import { PublicacionControl } from '../../../shared/publicacion-control';
import { PublicacionCreate } from '../../../../data/api/generated-api.models';
import { CHART_PALETTE } from '../../../shared/chart-palette';
import { exportChart } from '../../../shared/export-chart';

@Component({
  selector: 'app-explorador',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent, BaseChartDirective],
  providers: [PublicacionControl],
  templateUrl: './explorador.html',
  styleUrls: ['./explorador.scss']
})
export class ExploradorComponent implements OnInit {
  exportarGrafica() { exportChart('#grafica-explorador canvas', 'explorador.png'); }
  // Opciones disponibles
  preguntasDisponibles: string[] = [];
  programasDisponibles: string[] = [];
  aniosDisponibles: number[] = [];
  momentosDisponibles: number[] = [0, 1, 5];

  // Filtros seleccionados
  preguntaSeleccionada: string = '';
  momentoSeleccionado: number | '' = '';
  programaSeleccionado: string = '';
  anioSeleccionado: number | '' = '';
  tipoGrafico: ChartType = 'bar';

  // Chart Data
  isChartReady = false;
  readonly publicacion = inject(PublicacionControl);
  chartData: ChartConfiguration['data'] = { labels: [], datasets: [] };
  chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' }
    }
  };

  constructor(private reportesApi: ReportesApi, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.publicacion.cargarPropias();
    this.cargarFiltrosIniciales();
  }

  cargarFiltrosIniciales() {
    this.reportesApi.exploradorInit().subscribe({
      next: (data) => {
        this.preguntasDisponibles = data.preguntas || [];
        this.programasDisponibles = data.programas || [];
        this.aniosDisponibles = data.anios || [];
        if (this.preguntasDisponibles.length > 0) {
          this.preguntaSeleccionada = this.preguntasDisponibles[0];
          this.generarGrafica();
        }
      },
      error: (err) => console.error("Error cargando filtros del explorador", err)
    });
  }

  generarGrafica() {
    if (!this.preguntaSeleccionada) return;
    
    this.isChartReady = false;
    this.reportesApi.explorar({
      pregunta: this.preguntaSeleccionada,
      momento: this.momentoSeleccionado === '' ? undefined : this.momentoSeleccionado,
      programa: this.programaSeleccionado || undefined,
      anio: this.anioSeleccionado === '' ? undefined : this.anioSeleccionado,
    }).subscribe({
      next: (data) => {
        this.chartData = {
          labels: data.labels,
          datasets: [
            {
              data: data.valores,
              label: 'Respuestas',
              backgroundColor: [...CHART_PALETTE],
              borderWidth: 1
            }
          ]
        };
        this.isChartReady = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error("Error generando gráfica", err);
        alert("Ocurrió un error al generar el reporte.");
      }
    });
  }

  get graficaKey(): string {
    const definicion = `${this.preguntaSeleccionada}|${this.momentoSeleccionado}|${this.programaSeleccionado}|${this.anioSeleccionado}`;
    let hash = 0;
    for (let i = 0; i < definicion.length; i++) hash = ((hash << 5) - hash + definicion.charCodeAt(i)) | 0;
    return `explorador_${Math.abs(hash).toString(36)}`;
  }

  publicar() {
    if (!confirm('Confirmo que revisé la privacidad de esta gráfica. Se publicarán métricas agregadas recalculadas por el sistema; las categorías con menos de 5 observaciones se agrupan u omiten.')) return;
    const payload: PublicacionCreate = {
      grafica_key: this.graficaKey,
      titulo: `Explorador: ${this.preguntaSeleccionada.slice(0, 150)}`,
      definicion: {
        origen: 'explorador', tipo_visualizacion: this.tipoGrafico as PublicacionCreate['definicion']['tipo_visualizacion'],
        pregunta: this.preguntaSeleccionada,
        momento: this.momentoSeleccionado === '' ? undefined : this.momentoSeleccionado as 0 | 1 | 5,
        programa: this.programaSeleccionado || undefined,
        anio: this.anioSeleccionado === '' ? undefined : this.anioSeleccionado,
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
