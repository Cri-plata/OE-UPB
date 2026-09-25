import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChartData, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';

import { PublicacionesApi } from '../../../../data/api/publicaciones.api';
import { PublicacionResponse } from '../../../../data/api/generated-api.models';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { CHART_PALETTE } from '../../../shared/chart-palette';


@Component({
  selector: 'app-publicaciones',
  standalone: true,
  imports: [CommonModule, BaseChartDirective, SidebarComponent],
  templateUrl: './publicaciones.html',
  styleUrls: ['./publicaciones.scss']
})
export class PublicacionesComponent implements OnInit {
  private readonly api = inject(PublicacionesApi);
  publicaciones: PublicacionResponse[] = [];
  cargando = true;
  error = '';

  ngOnInit(): void {
    this.api.listarAutorizadas().subscribe({
      next: publicaciones => {
        this.publicaciones = publicaciones;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No fue posible cargar las gráficas publicadas.';
        this.cargando = false;
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
