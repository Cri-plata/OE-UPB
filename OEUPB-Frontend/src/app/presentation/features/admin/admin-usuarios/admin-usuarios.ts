import { AuthImplementationRepository } from '../../../../data/repositories/auth-implementation.repository';
﻿import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import {
  UsuarioResponse as UsuarioResponseDto,
  UsuarioCreateRequest as UsuarioCreateDto
} from '../../../../data/api/generated-api.models';
import { SedesApi } from '../../../../data/api/sedes.api';
import { UsuariosApi } from '../../../../data/api/usuarios.api';

interface SedeDto { id: number; codigo: string; nombre: string; }
type PermisoConsulta = NonNullable<UsuarioCreateDto['permisos']>[number];

function upbEmailValidator(control: any) {
  const email = control.value;
  if (email && !email.endsWith('@upb.edu.co')) {
    return { notUpb: true };
  }
  return null;
}
@Component({
  selector: 'app-admin-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, SidebarComponent],
  templateUrl: './admin-usuarios.html',
  styleUrls: ['./admin-usuarios.scss']
})

export class AdminUsuariosComponent implements OnInit {
  userForm: FormGroup;
  usuarios: UsuarioResponseDto[] = [];
  usuariosFiltrados: UsuarioResponseDto[] = [];
  terminoBusqueda: string = '';
  filtroRol: string = '';
  filtroSede: string = '';
  filtroAlcance: string = '';
  filtroEstado: string = '';
  private authRepo = inject(AuthImplementationRepository);
  private usuariosApi = inject(UsuariosApi);
  private sedesApi = inject(SedesApi);
  usuarioActual: any = null;
  catalogoSedes: SedeDto[] = [];
  sedesDisponibles: SedeDto[] = [];
  credencialTemporal: { correo: string; contrasena: string; expiraEn?: string | null } | null = null;
  programasDisponibles: string[] = [];
  /** Programas de la cuenta en edición que ya no se observan en cargas (PRG-01); se conservan como opción. */
  programasSinDatos: string[] = [];
  usuarioEditandoId: number | null = null;
  readonly permisosDisponibles: ReadonlyArray<{ id: PermisoConsulta; nombre: string }> = [
    { id: 'ver_reporte_general', nombre: 'Reporte general' },
    { id: 'ver_tendencias', nombre: 'Tendencias' },
    { id: 'ver_explorador', nombre: 'Explorador' },
    { id: 'ver_publicaciones', nombre: 'Publicaciones' }
  ];

  constructor(private fb: FormBuilder, private cdr: ChangeDetectorRef) {
    this.userForm = this.fb.group({
      nombre: ['', Validators.required],
      correo: ['', [Validators.required, Validators.email, upbEmailValidator]],
      // ADR-017: letras y números; el backend ignora espacios, puntos y guiones.
      numero_documento: ['', [Validators.pattern(/^[A-Za-z0-9 .-]{5,40}$/)]],
      sede_id: [null],
      rol: ['', Validators.required],
      etiqueta: [''],
      permisos: this.fb.group({
        ver_reporte_general: [false],
        ver_tendencias: [false],
        ver_explorador: [false],
        ver_publicaciones: [false]
      }),
      programas: [[]]
    });
  }

  ngOnInit() {
    this.usuarioActual = this.authRepo.getUsuarioActual();
    this.sedesApi.listar().subscribe({
      next: sedes => {
        this.catalogoSedes = sedes;
        this.sedesDisponibles = this.usuarioActual.rol === 'Admin_CTIC'
          ? sedes
          : sedes.filter(s => s.id === this.usuarioActual.sedeId);
        if (this.sedesDisponibles.length === 1) {
          this.userForm.patchValue({ sede_id: this.sedesDisponibles[0].id });
        }
      },
      error: err => console.error('Error cargando catálogo de sedes', err)
    });
    if (this.usuarioActual.rol === 'Admin_CTIC') {
      this.userForm.patchValue({ rol: 'Coordinador_Sede' });
    } else if (this.usuarioActual.rol === 'Coordinador_Sede') {
      this.userForm.patchValue({ rol: 'Usuario_Consulta' });
      this.usuariosApi.programasAsignables().subscribe({
        next: programas => this.programasDisponibles = programas,
        error: err => console.error('Error cargando programas asignables', err)
      });
    }
    this.cargarUsuarios();
  }

  cargarUsuarios() {
    this.usuariosApi.listar().subscribe({
      next: (data) => {
        this.usuarios = data.filter(u => u.rol !== 'Admin_CTIC');
        this.aplicarFiltros();
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error cargando usuarios', err)
    });
  }

  get sedesParaFiltro(): SedeDto[] {
    return this.catalogoSedes.length > 0 ? this.catalogoSedes : this.sedesDisponibles;
  }

  get rolesDisponibles(): string[] {
    const roles = new Set(this.usuarios.map(u => u.rol));
    roles.add('Coordinador_Sede');
    roles.add('Usuario_Consulta');
    return Array.from(roles);
  }

  get mostrarFiltroRol(): boolean {
    return true;
  }

  get mostrarFiltroSede(): boolean {
    return true;
  }

  get alcancesDisponibles(): string[] {
    const alcances = new Set<string>();
    for (const u of this.usuarios) {
      if (u.etiqueta) alcances.add(u.etiqueta);
    }
    const defaultAlcances = ['Rector', 'Profesor', 'Administrativo'];
    for (const a of defaultAlcances) {
      alcances.add(a);
    }
    return Array.from(alcances);
  }

  get mostrarFiltroAlcance(): boolean {
    return true;
  }

  // Alias retrocompatibles
  get perfilesDisponibles(): string[] {
    return this.alcancesDisponibles;
  }

  get mostrarFiltroPerfil(): boolean {
    return true;
  }

  get filtroPerfil(): string {
    return this.filtroAlcance;
  }

  set filtroPerfil(val: string) {
    this.filtroAlcance = val;
  }

  get hayFiltrosActivos(): boolean {
    return !!(
      this.terminoBusqueda.trim() ||
      this.filtroRol ||
      this.filtroSede !== '' ||
      this.filtroAlcance ||
      this.filtroEstado !== ''
    );
  }

  onBusquedaChange() {
    this.aplicarFiltros();
  }

  limpiarBusqueda() {
    this.terminoBusqueda = '';
    this.aplicarFiltros();
  }

  limpiarFiltros() {
    this.terminoBusqueda = '';
    this.filtroRol = '';
    this.filtroSede = '';
    this.filtroAlcance = '';
    this.filtroEstado = '';
    this.aplicarFiltros();
  }

  aplicarFiltros() {
    const q = this.normalizarTexto(this.terminoBusqueda);
    this.usuariosFiltrados = this.usuarios.filter(u => {
      if (q) {
        const coincideNombre = this.normalizarTexto(u.nombre).includes(q);
        const coincideCorreo = this.normalizarTexto(u.correo).includes(q);
        const coincideId = String(u.id).includes(q);
        const coincideSede = this.normalizarTexto(this.nombreSede(u.sede_id)).includes(q);
        const coincideEtiqueta = this.normalizarTexto(u.etiqueta).includes(q);
        const coincideProgramas = (u.programas || []).some(p => this.normalizarTexto(p).includes(q));
        if (!coincideNombre && !coincideCorreo && !coincideId && !coincideSede && !coincideEtiqueta && !coincideProgramas) {
          return false;
        }
      }

      if (this.filtroRol && u.rol !== this.filtroRol) {
        return false;
      }

      if (this.filtroSede !== '' && u.sede_id !== Number(this.filtroSede)) {
        return false;
      }

      if (this.filtroAlcance && u.etiqueta !== this.filtroAlcance) {
        return false;
      }

      if (this.filtroEstado === 'activo' && !u.activo) {
        return false;
      }
      if (this.filtroEstado === 'inactivo' && u.activo) {
        return false;
      }

      return true;
    });
    this.cdr.detectChanges();
  }

  private normalizarTexto(texto: string | null | undefined): string {
    return (texto || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim();
  }

  onSubmit() {
    if (this.userForm.valid) {
      const formValue = this.userForm.value;
      if (this.usuarioEditandoId === null && !formValue.numero_documento) {
        alert('El número de documento es obligatorio para la credencial inicial.');
        return;
      }
      if (formValue.rol === 'Coordinador_Sede' && !formValue.sede_id) {
        alert('Los Coordinadores de Sede deben tener una sede asignada obligatoriamente.');
        return;
      }
      const nuevoUsuario: UsuarioCreateDto = {
        nombre: formValue.nombre,
        correo: formValue.correo,
        numero_documento: formValue.numero_documento,
        rol: formValue.rol,
        sede_id: formValue.sede_id,
        etiqueta: formValue.etiqueta || null,
        permisos: Object.entries(formValue.permisos || {})
          .filter(([, habilitado]) => habilitado)
          .map(([permiso]) => permiso as PermisoConsulta),
        programas: formValue.programas || []
      };

      if (this.usuarioEditandoId !== null) {
        const cambios = this.usuarioActual?.rol === 'Admin_CTIC'
          ? { nombre: formValue.nombre, sede_id: formValue.sede_id }
          : {
              nombre: formValue.nombre,
              etiqueta: formValue.etiqueta || null,
              permisos: nuevoUsuario.permisos,
              programas: nuevoUsuario.programas
            };
        this.usuariosApi.actualizar(this.usuarioEditandoId, cambios).subscribe({
          next: actualizado => {
            const indice = this.usuarios.findIndex(u => u.id === actualizado.id);
            if (indice >= 0) this.usuarios[indice] = actualizado;
            this.usuarioEditandoId = null;
            this.restablecerFormulario();
            this.aplicarFiltros();
            this.cdr.detectChanges();
          },
          error: err => alert('Error: ' + (err.error?.detail || 'No se pudo actualizar el usuario'))
        });
        return;
      }

      this.usuariosApi.crear(nuevoUsuario).subscribe({
        next: (response) => {
          this.usuarios.push(response);
          this.credencialTemporal = {
            correo: response.correo,
            contrasena: response.contrasena_temporal,
            expiraEn: response.credencial_temporal_expira_en
          };
          this.aplicarFiltros();
          this.cdr.detectChanges(); // Agregar a la tabla en vivo
          this.restablecerFormulario();
        },
        error: (err) => {
          alert('Error: ' + (err.error?.detail || 'No se pudo crear el usuario'));
        }
      });
    } else {
      this.userForm.markAllAsTouched();
    }
  }

  cambiarEstado(usuario: UsuarioResponseDto) {
    const accion = usuario.activo ? 'desactivar' : 'reactivar';
    if (!confirm(`¿Deseas ${accion} la cuenta de ${usuario.nombre}?`)) return;
    this.usuariosApi.cambiarEstado(usuario.id, accion).subscribe({
      next: actualizado => {
        const indice = this.usuarios.findIndex(u => u.id === actualizado.id);
        if (indice >= 0) this.usuarios[indice] = actualizado;
        this.aplicarFiltros();
        this.cdr.detectChanges();
      },
      error: err => alert('Error: ' + (err.error?.detail || 'No se pudo cambiar el estado'))
    });
  }

  editarUsuario(usuario: UsuarioResponseDto) {
    this.usuarioEditandoId = usuario.id;
    this.programasSinDatos = usuario.programas_sin_datos ?? [];
    this.userForm.patchValue({
      nombre: usuario.nombre,
      correo: usuario.correo,
      numero_documento: '',
      sede_id: usuario.sede_id,
      rol: usuario.rol,
      etiqueta: usuario.etiqueta || '',
      permisos: Object.fromEntries(this.permisosDisponibles.map(p => [p.id, usuario.permisos.includes(p.id)])),
      programas: usuario.programas
    });
  }

  cancelarEdicion() {
    this.usuarioEditandoId = null;
    this.restablecerFormulario();
  }

  private restablecerFormulario() {
    this.programasSinDatos = [];
    this.userForm.reset({
      numero_documento: '',
      sede_id: this.sedesDisponibles.length === 1 ? this.sedesDisponibles[0].id : null,
      rol: this.usuarioActual?.rol === 'Admin_CTIC' ? 'Coordinador_Sede' : 'Usuario_Consulta',
      etiqueta: '',
      permisos: {
        ver_reporte_general: false,
        ver_tendencias: false,
        ver_explorador: false,
        ver_publicaciones: false
      },
      programas: []
    });
  }

  nombreSede(sedeId: number | null | undefined): string {
    const sede = this.catalogoSedes.find(s => s.id === sedeId) || this.sedesDisponibles.find(s => s.id === sedeId);
    return sede?.nombre || (sedeId ? `Sede ${sedeId}` : 'N/A');
  }

  async copiarContrasenaTemporal() {
    if (this.credencialTemporal) {
      await navigator.clipboard.writeText(this.credencialTemporal.contrasena);
    }
  }

  cerrarCredencialTemporal() {
    this.credencialTemporal = null;
  }
  regenerarCredencial(usuario: UsuarioResponseDto) {
    const motivo = prompt('Motivo de recuperación o reemisión (mínimo 10 caracteres):');
    if (!motivo) return;
    this.usuariosApi.regenerarCredencial(usuario.id, motivo).subscribe({
      next: response => {
        const indice = this.usuarios.findIndex(u => u.id === response.usuario.id);
        if (indice >= 0) this.usuarios[indice] = response.usuario;
        this.credencialTemporal = {
          correo: response.usuario.correo,
          contrasena: response.contrasena_temporal,
          expiraEn: response.credencial_temporal_expira_en
        };
        this.aplicarFiltros();
        this.cdr.detectChanges();
      },
      error: err => alert('Error: ' + (err.error?.detail || 'No se pudo regenerar la credencial'))
    });
  }
  eliminarUsuario(id: number) {
    if (confirm('¿Deseas desactivar este usuario? La cuenta podrá reactivarse.')) {
      this.usuariosApi.desactivar(id).subscribe({
        next: () => {
          const usuario = this.usuarios.find(u => u.id === id);
          if (usuario) usuario.activo = false;
          this.aplicarFiltros();
          this.cdr.detectChanges();
        },
        error: (err) => alert('Error eliminando: ' + (err.error?.detail || 'Fallo desconocido'))
      });
    }
  }
}




