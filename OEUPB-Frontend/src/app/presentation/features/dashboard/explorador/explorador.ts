import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { HttpClient } from '@angular/common/http';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartType } from 'chart.js';

@Component({
  selector: 'app-explorador',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent, BaseChartDirective],
  templateUrl: './explorador.html',
  styleUrls: ['./explorador.scss']
})
export class ExploradorComponent implements OnInit {
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
  chartData: ChartConfiguration['data'] = { labels: [], datasets: [] };
  chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' }
    }
  };

  private readonly API_URL = 'http://localhost:8000/api/reportes/explorador';
  private readonly INIT_URL = 'http://localhost:8000/api/reportes/explorador/init';

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.cargarFiltrosIniciales();
  }

  cargarFiltrosIniciales() {
    this.http.get<any>(this.INIT_URL).subscribe({
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
    let url = `${this.API_URL}?pregunta=${encodeURIComponent(this.preguntaSeleccionada)}`;
    if (this.momentoSeleccionado !== '') url += `&momento=${this.momentoSeleccionado}`;
    if (this.programaSeleccionado !== '') url += `&programa=${encodeURIComponent(this.programaSeleccionado)}`;
    if (this.anioSeleccionado !== '') url += `&anio=${this.anioSeleccionado}`;

    this.http.get<any>(url).subscribe({
      next: (data) => {
        this.chartData = {
          labels: data.labels,
          datasets: [
            {
              data: data.valores,
              label: 'Respuestas',
              backgroundColor: [
                '#E63946', '#1D3557', '#2A9D8F', '#F4A261', '#9B5DE5',
                '#0077B6', '#00B4D8', '#90E0EF', '#CAF0F8', '#FFB703'
              ],
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
}
