import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DirectorioApi } from '../../../../data/api/directorio.api';
import { DirectorioItem } from '../../../../data/api/generated-api.models';

@Component({
  selector: 'app-directorio',
  standalone: true,
  imports: [CommonModule, SidebarComponent, FormsModule],
  templateUrl: './directorio.html',
  styleUrls: ['./directorio.scss']
})
export class DirectorioComponent implements OnInit {
  terminoBusqueda: string = '';
  programaSeleccionado: string = '';
  
  // Signals: la aplicación es zoneless y la vista debe reflejar la respuesta sin otra interacción.
  readonly programasDisponibles = signal<string[]>([]);
  readonly egresados = signal<DirectorioItem[]>([]);
  
  paginaActual: number = 1;
  readonly totalRegistros = signal(0);
  registrosPorPagina: number = 50;
  
  readonly cargando = signal(false);
  readonly mostrandoFormulario = signal(false);
  readonly editandoDocumento = signal<string | null>(null);
  readonly mensaje = signal('');
  readonly error = signal('');
  formulario = { numero_documento: '', primer_nombre: '', primer_apellido: '', programa: '', fecha_grado: '', motivo: '' };

  constructor(private directorioApi: DirectorioApi, private router: Router) {}

  ngOnInit() {
    this.cargarProgramas();
    this.buscar();
  }

  cargarProgramas() {
    this.directorioApi.programas().subscribe(data => this.programasDisponibles.set(data));
  }

  buscar() {
    this.cargando.set(true);
    this.directorioApi.buscar(
      this.paginaActual,
      this.registrosPorPagina,
      this.terminoBusqueda.trim() || undefined,
      this.programaSeleccionado || undefined,
    ).subscribe({
      next: (res) => {
        this.egresados.set(res.data);
        this.totalRegistros.set(res.total);
        this.cargando.set(false);
      },
      error: () => this.cargando.set(false)
    });
  }

  onFiltroChange() {
    this.paginaActual = 1;
    this.buscar();
  }

  cambiarPagina(delta: number) {
    const nuevaPagina = this.paginaActual + delta;
    if (nuevaPagina >= 1 && nuevaPagina <= this.getTotalPaginas()) {
      this.paginaActual = nuevaPagina;
      this.buscar();
    }
  }

  getTotalPaginas(): number {
    return Math.ceil(this.totalRegistros() / this.registrosPorPagina);
  }

  verPerfil(documento: string) {
    this.router.navigate(['/perfil', documento]);
  }

  nuevo() {
    this.editandoDocumento.set(null);
    this.formulario = { numero_documento: '', primer_nombre: '', primer_apellido: '', programa: '', fecha_grado: '', motivo: 'Registro manual autorizado' };
    this.mostrandoFormulario.set(true);
  }

  editar(e: DirectorioItem, event: Event) {
    event.stopPropagation();
    const [primer_nombre, ...resto] = e.nombre_completo.split(' ');
    this.editandoDocumento.set(e.documento);
    this.formulario = { numero_documento: e.documento, primer_nombre, primer_apellido: resto.join(' '), programa: e.programa || '', fecha_grado: e.fecha_grado === 'N/A' ? '' : e.fecha_grado, motivo: 'Corrección manual autorizada' };
    this.mostrandoFormulario.set(true);
  }

  guardar() {
    this.error.set('');
    const payload = { ...this.formulario, fecha_grado: this.formulario.fecha_grado || null };
    const editando = this.editandoDocumento();
    const operacion = editando
      ? this.directorioApi.editar(editando, payload)
      : this.directorioApi.crear(payload);
    operacion.subscribe({
      next: () => { this.mostrandoFormulario.set(false); this.mensaje.set('Registro guardado correctamente.'); this.cargarProgramas(); this.buscar(); },
      error: (err) => this.error.set(err.error?.detail || 'No fue posible guardar el registro.')
    });
  }

  eliminar(e: DirectorioItem, event: Event) {
    event.stopPropagation();
    const motivo = window.prompt('Motivo de eliminación (mínimo 5 caracteres):');
    if (!motivo) return;
    this.directorioApi.eliminar(e.documento, motivo).subscribe({
      next: () => { this.mensaje.set('Registro eliminado correctamente.'); this.buscar(); },
      error: (err) => this.error.set(err.error?.detail || 'No fue posible eliminar el registro.')
    });
  }

  exportar() {
    this.directorioApi.exportar(this.terminoBusqueda.trim() || undefined, this.programaSeleccionado || undefined).subscribe(blob => {
      const enlace = document.createElement('a');
      enlace.href = URL.createObjectURL(blob);
      enlace.download = 'directorio-egresados.xlsx';
      enlace.click();
      URL.revokeObjectURL(enlace.href);
    });
  }
}


