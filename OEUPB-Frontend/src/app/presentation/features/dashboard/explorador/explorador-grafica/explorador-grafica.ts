import { Component, OnInit, computed, inject, input, output, signal } from '@angular/core';
import { SlicePipe } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartType } from 'chart.js';

import { ReportesApi } from '../../../../../data/api/reportes.api';
import { ExploradorInitResponse, PublicacionCreate } from '../../../../../data/api/generated-api.models';
import { PublicacionControl } from '../../../../shared/publicacion-control';
import { CHART_PALETTE } from '../../../../shared/chart-palette';
import { exportChart } from '../../../../shared/export-chart';
import { hashCorto } from '../../../../shared/filtros-grafica';
import { mensajeDeError } from '../../../../shared/mensaje-error';

/**
 * Un bloque independiente del Explorador (EXP-03): conserva su propia variable,
 * filtros, tipo de gráfica, estado de carga/error y publicación.
 */
@Component({
  selector: 'app-explorador-grafica',
  standalone: true,
  imports: [SlicePipe, BaseChartDirective],
  templateUrl: './explorador-grafica.html',
  styleUrls: ['../explorador.scss']
})
export class ExploradorGraficaComponent implements OnInit {
  private readonly reportesApi = inject(ReportesApi);
  /** Provisto por el Explorador: una sola solicitud de publicación a la vez en la página. */
  readonly publicacion = inject(PublicacionControl);

  readonly numero = input.required<number>();
  readonly opciones = input.required<ExploradorInitResponse>();
  readonly puedeQuitar = input(false);
  readonly quitar = output<void>();

  readonly momentosDisponibles = [0, 1, 5];
  readonly pregunta = signal('');
  readonly momento = signal<number | undefined>(undefined);
  readonly programa = signal('');
  readonly anio = signal<number | undefined>(undefined);
  readonly tipo = signal<ChartType>('bar');

  readonly cargando = signal(false);
  readonly error = signal('');
  readonly chartData = signal<ChartConfiguration['data'] | null>(null);
  readonly chartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'bottom' } }
  };

  readonly idGrafica = computed(() => `grafica-explorador-${this.numero()}`);
  readonly graficaKey = computed(() =>
    `explorador_${hashCorto(`${this.pregunta()}|${this.momento() ?? ''}|${this.programa()}|${this.anio() ?? ''}`)}`
  );

  ngOnInit(): void {
    const preguntas = this.opciones().preguntas;
    if (preguntas.length) {
      this.pregunta.set(preguntas[0]);
      this.generar();
    }
  }

  cambiar(campo: 'pregunta' | 'momento' | 'programa' | 'anio', valor: string): void {
    if (campo === 'pregunta') this.pregunta.set(valor);
    if (campo === 'momento') this.momento.set(valor === '' ? undefined : Number(valor));
    if (campo === 'programa') this.programa.set(valor);
    if (campo === 'anio') this.anio.set(valor === '' ? undefined : Number(valor));
    this.generar();
  }

  cambiarTipo(valor: string): void {
    this.tipo.set(valor as ChartType);
  }

  generar(): void {
    if (!this.pregunta()) return;
    this.cargando.set(true);
    this.error.set('');
    this.reportesApi.explorar({
      pregunta: this.pregunta(),
      momento: this.momento(),
      programa: this.programa() || undefined,
      anio: this.anio(),
    }).subscribe({
      next: datos => {
        this.chartData.set({
          labels: datos.labels,
          datasets: [{ data: datos.valores, label: 'Respuestas', backgroundColor: [...CHART_PALETTE], borderWidth: 1 }]
        });
        this.cargando.set(false);
      },
      error: (err: unknown) => {
        this.chartData.set(null);
        this.error.set(mensajeDeError(err, 'No fue posible generar la gráfica.'));
        this.cargando.set(false);
      }
    });
  }

  exportar(): void {
    exportChart(`#${this.idGrafica()} canvas`, `explorador-${this.numero()}.png`);
  }

  publicar(): void {
    if (!confirm('Confirmo que revisé la privacidad de esta gráfica. Se publicarán métricas agregadas recalculadas por el sistema; las categorías con menos de 5 observaciones se agrupan u omiten.')) return;
    const payload: PublicacionCreate = {
      grafica_key: this.graficaKey(),
      titulo: `Explorador: ${this.pregunta().slice(0, 150)}`,
      definicion: {
        origen: 'explorador',
        tipo_visualizacion: this.tipo() as PublicacionCreate['definicion']['tipo_visualizacion'],
        pregunta: this.pregunta(),
        momento: this.momento() as 0 | 1 | 5 | undefined,
        programa: this.programa() || undefined,
        anio: this.anio(),
      },
      aprobada_privacidad: true
    };
    this.publicacion.publicar(payload.grafica_key, payload);
  }

  retirar(): void {
    if (!confirm('¿Retirar esta publicación? Dejará de ser visible inmediatamente.')) return;
    this.publicacion.retirar(this.graficaKey());
  }
}
