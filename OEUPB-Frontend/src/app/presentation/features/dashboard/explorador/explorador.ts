import { Component, OnInit, inject, signal } from '@angular/core';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { ReportesApi } from '../../../../data/api/reportes.api';
import { PublicacionControl } from '../../../shared/publicacion-control';
import { ExploradorInitResponse } from '../../../../data/api/generated-api.models';
import { mensajeDeError } from '../../../shared/mensaje-error';
import { ExploradorGraficaComponent } from './explorador-grafica/explorador-grafica';

/** Explorador con varias gráficas simultáneas para comparar (EXP-03). */
@Component({
  selector: 'app-explorador',
  standalone: true,
  imports: [SidebarComponent, ExploradorGraficaComponent],
  providers: [PublicacionControl],
  templateUrl: './explorador.html',
  styleUrls: ['./explorador.scss']
})
export class ExploradorComponent implements OnInit {
  private readonly reportesApi = inject(ReportesApi);
  readonly publicacion = inject(PublicacionControl);

  readonly opciones = signal<ExploradorInitResponse | null>(null);
  readonly error = signal('');
  /** Identificadores estables de los bloques visibles. */
  readonly bloques = signal<number[]>([1]);
  private siguienteId = 2;

  ngOnInit() {
    this.publicacion.cargarPropias();
    this.cargarOpciones();
  }

  cargarOpciones() {
    this.error.set('');
    this.reportesApi.exploradorInit().subscribe({
      next: opciones => this.opciones.set(opciones),
      error: (err: unknown) => this.error.set(mensajeDeError(err, 'No fue posible cargar las variables del explorador.'))
    });
  }

  crearOtra() {
    this.bloques.update(bloques => [...bloques, this.siguienteId++]);
  }

  quitar(id: number) {
    this.bloques.update(bloques => bloques.length > 1 ? bloques.filter(bloque => bloque !== id) : bloques);
  }
}
