import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LoginUseCase } from '../../../../domain/usecases/login.usecase';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.scss']
})
export class LoginComponent {
  loginForm: FormGroup;
  cambioForm: FormGroup;
  errorMessage: string | null = null;
  cambioError: string | null = null;
  isLoading = false;
  isChangingPassword = false;
  mostrarCambioObligatorio = false;

  private fb = inject(FormBuilder);
  private loginUseCase = inject(LoginUseCase);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  constructor() {
    this.loginForm = this.fb.group({
      correo: ['', [Validators.required, Validators.email]],
      contrasena: ['', [Validators.required, Validators.minLength(6)]]
    });
    this.cambioForm = this.fb.group({
      nuevaContrasena: ['', [Validators.required, Validators.minLength(10)]],
      confirmarContrasena: ['', [Validators.required, Validators.minLength(10)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = null;

    const { correo, contrasena } = this.loginForm.value;

    this.loginUseCase.execute(correo, contrasena).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.cdr.detectChanges();
        if (response.usuario.debeCambiarContrasena) {
          this.mostrarCambioObligatorio = true;
          this.cdr.detectChanges();
          return;
        }
        this.redirigirPorRol(response.usuario.rol);
      },
      error: (err) => {
        this.isLoading = false;
        this.cdr.detectChanges();
        const detail = err.error?.detail;
        this.errorMessage = detail?.codigo === 'CREDENCIAL_TEMPORAL_VENCIDA'
          ? detail.mensaje
          : 'Correo o contraseña no válido. Intente de nuevo.';
        this.cdr.detectChanges();
      }
    });
  }

  cambiarContrasena(): void {
    if (this.cambioForm.invalid) {
      this.cambioForm.markAllAsTouched();
      return;
    }

    const { nuevaContrasena, confirmarContrasena } = this.cambioForm.value;
    this.cambioError = null;
    this.isChangingPassword = true;

    try {
      this.loginUseCase.cambiarContrasenaTemporal(nuevaContrasena, confirmarContrasena).subscribe({
        next: (response) => {
          this.isChangingPassword = false;
          this.mostrarCambioObligatorio = false;
          this.cdr.detectChanges();
          this.redirigirPorRol(response.usuario.rol);
        },
        error: (err) => {
          this.isChangingPassword = false;
          this.cambioError = err.error?.detail || 'No se pudo cambiar la contraseña.';
          this.cdr.detectChanges();
        }
      });
    } catch (error: any) {
      this.isChangingPassword = false;
      this.cambioError = error.message;
    }
  }

  private redirigirPorRol(rol: string): void {
    if (rol === 'Admin_CTIC') {
      this.router.navigate(['/admin-usuarios']);
    } else if (rol === 'Usuario_Consulta') {
      this.router.navigate(['/mi-perfil']);
    } else {
      this.router.navigate(['/reporte']);
    }
  }
}





