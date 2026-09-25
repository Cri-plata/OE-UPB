import { Component, OnInit, computed, inject, input, output, signal } from '@angular/core';

import { FiltrosAnaliticos, ReportesApi } from '../../../../data/api/reportes.api';
import { mensajeDeError } from '../../mensaje-error';

/**
 * Filtros multiselección de programa y cohorte del dashboard privado (HU-09).
 * Las opciones provienen del backend (datos de la sede autenticada).
 */
@Component({
  selector: 'app-filtros-analiticos',
  standalone: true,
  templateUrl: './filtros-analiticos.html',
  styleUrls: ['./filtros-analiticos.scss']
})
export class FiltrosAnaliticosComponent implements OnInit {
  private readonly api = inject(ReportesApi);

  /** Muestra el selector de momento (Reporte General). */
  readonly conMomento = input(false);
  readonly aplicar = output<FiltrosAnaliticos>();

  readonly programasDisponibles = signal<string[]>([]);
  readonly aniosDisponibles = signal<number[]>([]);
  readonly error = signal('');

  readonly programas = signal<string[]>([]);
  readonly anios = signal<number[]>([]);
  readonly momento = signal<number | undefined>(undefined);
  readonly activos = computed(() => this.programas().length + this.anios().length + (this.momento() === undefined ? 0 : 1));

  ngOnInit(): void {
    this.api.filtros().subscribe({
      next: filtros => {
        this.programasDisponibles.set(filtros.programas);
        this.aniosDisponibles.set(filtros.anios);
      },
      error: (error: unknown) => this.error.set(mensajeDeError(error, 'No fue posible cargar los filtros.')),
    });
  }

  alternarPrograma(programa: string, marcado: boolean): void {
    this.programas.update(actuales => marcado ? [...actuales, programa] : actuales.filter(p => p !== programa));
  }

  alternarAnio(anio: number, marcado: boolean): void {
    this.anios.update(actuales => marcado ? [...actuales, anio] : actuales.filter(a => a !== anio));
  }

  cambiarMomento(valor: string): void {
    this.momento.set(valor === '' ? undefined : Number(valor));
  }

  emitir(): void {
    this.aplicar.emit({ programas: [...this.programas()].sort(), anios: [...this.anios()].sort(), momento: this.momento() });
  }

  limpiar(): void {
    this.programas.set([]);
    this.anios.set([]);
    this.momento.set(undefined);
    this.emitir();
  }
}
