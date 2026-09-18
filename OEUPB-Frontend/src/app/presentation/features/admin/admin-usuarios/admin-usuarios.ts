import { AuthImplementationRepository } from '../../../../data/repositories/auth-implementation.repository';
﻿import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SidebarComponent } from '../../../shared/components/sidebar/sidebar';
import { HttpClient } from '@angular/common/http';
import { UsuarioResponseDto, UsuarioCreateDto } from '../../../../../../../OEUPB-Contracts/APIcontractfront/admin.contract';

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
  imports: [CommonModule, ReactiveFormsModule, SidebarComponent],
  templateUrl: './admin-usuarios.html',
  styleUrls: ['./admin-usuarios.scss']
})

export class AdminUsuariosComponent implements OnInit {
  userForm: FormGroup;
  usuarios: UsuarioResponseDto[] = [];
  private readonly API_URL = 'http://localhost:8000/api/usuarios';

  private authRepo = inject(AuthImplementationRepository);
  usuarioActual: any = null;
  sedesDisponibles: string[] = [];

  constructor(private fb: FormBuilder, private http: HttpClient, private cdr: ChangeDetectorRef) {
    this.userForm = this.fb.group({
      nombre: ['', Validators.required],
      correo: ['', [Validators.required, Validators.email, upbEmailValidator]],
      sede: [''],
      rol: ['', Validators.required]
    });
  }

  ngOnInit() {
    this.usuarioActual = this.authRepo.getUsuarioActual();
    const mapaSedes: any = { 1: 'Bucaramanga', 2: 'Medellín', 3: 'Palmira', 4: 'Montería', 5: 'Bogotá' };
    if (this.usuarioActual.rol === 'Admin_CTIC') {
      this.sedesDisponibles = ['Bucaramanga', 'Medellín', 'Palmira', 'Montería', 'Bogotá'];
    } else if (this.usuarioActual.rol === 'Coordinador_Sede' && this.usuarioActual.sedeId) {
      this.sedesDisponibles = [mapaSedes[this.usuarioActual.sedeId]];
    }
    if (this.sedesDisponibles.length === 1) {
      this.userForm.patchValue({ sede: this.sedesDisponibles[0] });
    }
    if (this.usuarioActual.rol === 'Admin_CTIC') {
      this.userForm.patchValue({ rol: 'Coordinador_Sede' });
    }
    this.cargarUsuarios();
  }

  cargarUsuarios() {
    this.http.get<UsuarioResponseDto[]>(this.API_URL).subscribe({
      next: (data) => {
        this.usuarios = data.filter(u => u.rol !== 'Admin_CTIC');
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error cargando usuarios', err)
    });
  }

  onSubmit() {
    if (this.userForm.valid) {
      const formValue = this.userForm.value;
      if (formValue.rol === 'Coordinador_Sede' && !formValue.sede) {
        alert('Los Coordinadores de Sede deben tener una sede asignada obligatoriamente.');
        return;
      }
      const nuevoUsuario: UsuarioCreateDto = {
        nombre: formValue.nombre,
        correo: formValue.correo,
        rol: formValue.rol,
        sede: formValue.sede
      };

      this.http.post<UsuarioResponseDto>(this.API_URL, nuevoUsuario).subscribe({
        next: (response) => {
                    const mapaSedes: any = { 1: 'Bucaramanga', 2: 'Medellín', 3: 'Palmira', 4: 'Montería', 5: 'Bogotá' };
          if (typeof response.sede_id === 'number') {
            response.sede_id = mapaSedes[response.sede_id];
          }
          this.usuarios.push(response);
          this.cdr.detectChanges(); // Agregar a la tabla en vivo
          this.userForm.reset();
          alert('¡Usuario guardado exitosamente en MySQL! Contraseña por defecto: upb123');
        },
        error: (err) => {
          alert('Error: ' + (err.error?.detail || 'No se pudo crear el usuario'));
        }
      });
    } else {
      this.userForm.markAllAsTouched();
    }
  }
  eliminarUsuario(id: number) {
    if (confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
      this.http.delete(`${this.API_URL}/${id}`).subscribe({
        next: () => {
          this.usuarios = this.usuarios.filter(u => u.id !== id);
          this.cdr.detectChanges();
        },
        error: (err) => alert('Error eliminando: ' + (err.error?.detail || 'Fallo desconocido'))
      });
    }
  }
}




