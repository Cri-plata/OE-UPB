import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { Router } from '@angular/router';
import { ChangeDetectorRef } from '@angular/core';
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
  
  programasDisponibles: string[] = [];
  egresados: DirectorioItem[] = [];
  
  paginaActual: number = 1;
  totalRegistros: number = 0;
  registrosPorPagina: number = 50;
  
  cargando: boolean = false;
  mostrandoFormulario = false;
  editandoDocumento: string | null = null;
  mensaje = '';
  error = '';
  formulario = { numero_documento: '', primer_nombre: '', primer_apellido: '', programa: '', fecha_grado: '', motivo: '' };

  constructor(private directorioApi: DirectorioApi, private cdr: ChangeDetectorRef, private router: Router) {}

  ngOnInit() {
    this.cargarProgramas();
    this.buscar();
  }

  cargarProgramas() {
    this.directorioApi.programas().subscribe(data => {
      this.programasDisponibles = data;
    });
  }

  buscar() {
    this.cargando = true;
    this.directorioApi.buscar(
      this.paginaActual,
      this.registrosPorPagina,
      this.terminoBusqueda.trim() || undefined,
      this.programaSeleccionado || undefined,
    ).subscribe({
      next: (res) => {
        this.egresados = res.data;
        this.totalRegistros = res.total;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.cargando = false;
        this.cdr.detectChanges();
      }
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
    return Math.ceil(this.totalRegistros / this.registrosPorPagina);
  }

  verPerfil(documento: string) {
    this.router.navigate(['/perfil', documento]);
  }

  nuevo() {
    this.editandoDocumento = null;
    this.formulario = { numero_documento: '', primer_nombre: '', primer_apellido: '', programa: '', fecha_grado: '', motivo: 'Registro manual autorizado' };
    this.mostrandoFormulario = true;
  }

  editar(e: DirectorioItem, event: Event) {
    event.stopPropagation();
    const [primer_nombre, ...resto] = e.nombre_completo.split(' ');
    this.editandoDocumento = e.documento;
    this.formulario = { numero_documento: e.documento, primer_nombre, primer_apellido: resto.join(' '), programa: e.programa || '', fecha_grado: e.fecha_grado === 'N/A' ? '' : e.fecha_grado, motivo: 'Corrección manual autorizada' };
    this.mostrandoFormulario = true;
  }

  guardar() {
    this.error = '';
    const payload = { ...this.formulario, fecha_grado: this.formulario.fecha_grado || null };
    const operacion = this.editandoDocumento
      ? this.directorioApi.editar(this.editandoDocumento, payload)
      : this.directorioApi.crear(payload);
    operacion.subscribe({
      next: () => { this.mostrandoFormulario = false; this.mensaje = 'Registro guardado correctamente.'; this.cargarProgramas(); this.buscar(); },
      error: (err) => { this.error = err.error?.detail || 'No fue posible guardar el registro.'; }
    });
  }

  eliminar(e: DirectorioItem, event: Event) {
    event.stopPropagation();
    const motivo = window.prompt('Motivo de eliminación (mínimo 5 caracteres):');
    if (!motivo) return;
    this.directorioApi.eliminar(e.documento, motivo).subscribe({
      next: () => { this.mensaje = 'Registro eliminado correctamente.'; this.buscar(); },
      error: (err) => { this.error = err.error?.detail || 'No fue posible eliminar el registro.'; }
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


