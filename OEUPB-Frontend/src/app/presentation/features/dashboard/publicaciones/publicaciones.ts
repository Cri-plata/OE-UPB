import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChartData, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';

import { PublicacionesApi } from '../../../../data/api/publicaciones.api';
import { PublicacionResponse } from '../../../../data/api/generated-api.models';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { CHART_PALETTE } from '../../../shared/chart-palette';
import { mensajeDeError } from '../../../shared/mensaje-error';


@Component({
  selector: 'app-publicaciones',
  standalone: true,
  imports: [CommonModule, BaseChartDirective, SidebarComponent],
  templateUrl: './publicaciones.html',
  styleUrls: ['./publicaciones.scss']
})
export class PublicacionesComponent implements OnInit {
  private readonly api = inject(PublicacionesApi);
  // Signals: la aplicación es zoneless y la vista debe reflejar la respuesta sin otra interacción.
  readonly publicaciones = signal<PublicacionResponse[]>([]);
  readonly cargando = signal(true);
  readonly error = signal('');

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set('');
    this.api.listarAutorizadas().subscribe({
      next: publicaciones => {
        this.publicaciones.set(publicaciones);
        this.cargando.set(false);
      },
      error: (error: unknown) => {
        this.publicaciones.set([]);
        this.error.set(mensajeDeError(error, 'No fue posible cargar las gráficas publicadas.'));
        this.cargando.set(false);
      }
    });
  }

  tipo(publicacion: PublicacionResponse): ChartType {
    return publicacion.definicion.tipo_visualizacion as ChartType;
  }

  datos(publicacion: PublicacionResponse): ChartData<ChartType, (number | null)[], string> {
    return {
      labels: publicacion.metricas.labels,
      datasets: publicacion.metricas.datasets.map(dataset => ({
        label: dataset.label,
        data: dataset.data,
        backgroundColor: dataset.backgroundColor ?? CHART_PALETTE[0],
        borderColor: dataset.borderColor ?? CHART_PALETTE[0],
      }))
    };
  }
}
