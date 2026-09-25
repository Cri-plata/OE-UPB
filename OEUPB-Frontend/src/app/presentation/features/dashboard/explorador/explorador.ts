import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { ReportesApi } from '../../../../data/api/reportes.api';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartType } from 'chart.js';
import { PublicacionesApi } from '../../../../data/api/publicaciones.api';
import { PublicacionCreate, PublicacionResponse } from '../../../../data/api/generated-api.models';
import { CHART_PALETTE } from '../../../shared/chart-palette';
import { exportChart } from '../../../shared/export-chart';

@Component({
  selector: 'app-explorador',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent, BaseChartDirective],
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
  publicaciones: Record<string, PublicacionResponse> = {};
  publicando = false;
  chartData: ChartConfiguration['data'] = { labels: [], datasets: [] };
  chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' }
    }
  };

  constructor(private reportesApi: ReportesApi, private cdr: ChangeDetectorRef, private publicacionesApi: PublicacionesApi) {}

  ngOnInit() {
    this.publicacionesApi.listarPropias().subscribe(publicaciones => {
      this.publicaciones = Object.fromEntries(publicaciones.map(publicacion => [publicacion.grafica_key, publicacion]));
    });
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
    if (!confirm('Confirmo que esta gráfica contiene únicamente métricas agregadas y está aprobada para publicación.')) return;
    const programas = this.programaSeleccionado ? [this.programaSeleccionado] : this.programasDisponibles;
    const payload: PublicacionCreate = {
      grafica_key: this.graficaKey,
      titulo: `Explorador: ${this.preguntaSeleccionada.slice(0, 150)}`,
      programas,
      definicion: {
        origen: 'explorador', tipo_visualizacion: this.tipoGrafico as PublicacionCreate['definicion']['tipo_visualizacion'],
        pregunta: this.preguntaSeleccionada,
        momento: this.momentoSeleccionado === '' ? undefined : this.momentoSeleccionado as 0 | 1 | 5,
        programa: this.programaSeleccionado || undefined,
        anio: this.anioSeleccionado === '' ? undefined : this.anioSeleccionado,
      },
      metricas: {
        labels: (this.chartData.labels ?? []).map(String),
        datasets: this.chartData.datasets.map(dataset => ({
          label: dataset.label || 'Respuestas',
          data: dataset.data.map(valor => typeof valor === 'number' ? valor : null),
          backgroundColor: Array.isArray(dataset.backgroundColor) ? dataset.backgroundColor.map(String) : (typeof dataset.backgroundColor === 'string' ? dataset.backgroundColor : undefined),
          borderColor: typeof dataset.borderColor === 'string' ? dataset.borderColor : undefined,
        }))
      },
      aprobada_privacidad: true
    };
    this.publicando = true;
    this.publicacionesApi.publicar(payload).subscribe({
      next: publicacion => { this.publicaciones[this.graficaKey] = publicacion; this.publicando = false; },
      error: () => { alert('No fue posible publicar la gráfica.'); this.publicando = false; }
    });
  }

  retirar() {
    const publicacion = this.publicaciones[this.graficaKey];
    if (!publicacion || !confirm('¿Retirar esta publicación?')) return;
    this.publicando = true;
    this.publicacionesApi.retirar(publicacion.id).subscribe({
      next: () => { delete this.publicaciones[this.graficaKey]; this.publicando = false; },
      error: () => { alert('No fue posible retirar la publicación.'); this.publicando = false; }
    });
  }
}
